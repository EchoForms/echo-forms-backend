import threading
import asyncio
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for form response processing"""
    
    def __init__(self):
        self.tasks = {}
    
    def add_task(self, task_id: str, task_func, *args, **kwargs):
        """Add a background task"""
        def run_task():
            try:
                logger.info(f"Starting background task: {task_id}")
                task_func(*args, **kwargs)
                logger.info(f"Completed background task: {task_id}")
            except Exception as e:
                logger.error(f"Background task {task_id} failed: {str(e)}")
        
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        self.tasks[task_id] = thread
        return thread

# Global background task manager
background_manager = BackgroundTaskManager()

def process_form_response_background(
    formResponseId: int,
    formId: int,
    formfeildId: int,
    responseText: Optional[str],
    file_content: Optional[bytes],
    file_name: Optional[str],
    file_content_type: Optional[str],
    question_number: int,
    responseTime: Optional[float],
    user_id: str,
    db_session_factory
):
    """
    Background task to process form response field
    This includes:
    1. File upload to B2
    2. Audio transcription
    3. Language detection and translation
    4. Sentiment analysis
    5. Category extraction
    6. Analytics processing
    """
    try:
        # Create a new database session for this background task
        db = db_session_factory()
        
        logger.info(f"Processing background task for formResponseId: {formResponseId}")
        
        # Import here to avoid circular imports
        from utils.b2 import upload_file_to_b2
        from utils.gemini import transcribe_audio_file as gemini_transcribe
        from utils.translation import detect_language_and_translate, extract_categories_from_text, analyze_sentiment
        from utils.analytics import process_response_for_analytics
        from models.form_response_field import FormResponseField
        from models.form_analytics import FormAnalytics
        
        voiceFileLink = None
        transcribed_text = None
        
        # 1. Handle file upload if present
        if file_content and file_name:
            try:
                voiceFileLink = upload_file_to_b2(file_content, file_name, file_content_type)
                logger.info(f"File uploaded successfully: {voiceFileLink}")
            except Exception as e:
                logger.error(f"File upload failed: {str(e)}")
        
        # 2. Transcribe audio if file was uploaded
        if file_content and voiceFileLink:
            try:
                transcribed_text = gemini_transcribe(file_content, file_name)
                logger.info(f"Transcription completed: {transcribed_text[:100] if transcribed_text else 'None'}...")
            except Exception as e:
                logger.error(f"Transcription failed: {str(e)}")
        
        # 3. Process text analysis (translation, sentiment, categories)
        translated_text = None
        categories = []
        sentiment = "neutral"
        language_code = "en"
        
        # Get the text to analyze (prefer transcribed_text over responseText)
        text_to_analyze = transcribed_text if transcribed_text else responseText
        
        if text_to_analyze:
            try:
                # Detect language and translate if needed
                translated_text, is_translated, language_code = detect_language_and_translate(text_to_analyze)
                logger.info(f"Language detection: {language_code}, Translated: {is_translated}")
                
                # Analyze sentiment
                sentiment = analyze_sentiment(text_to_analyze)
                logger.info(f"Sentiment analysis: {sentiment}")
                
                # Extract categories from the text
                categories = extract_categories_from_text(text_to_analyze)
                logger.info(f"Extracted {len(categories)} categories")
                
            except Exception as e:
                logger.error(f"Text analysis failed: {str(e)}")
        
        # 4. Update the database record with processed data
        try:
            # Get the existing record
            field = db.query(FormResponseField).filter(
                FormResponseField.formResponseId == formResponseId,
                FormResponseField.formfeildId == formfeildId
            ).first()
            
            if field:
                # Update the record with processed data
                field.voiceFileLink = voiceFileLink
                field.transcribed_text = transcribed_text
                field.translated_text = translated_text
                field.categories = categories
                field.sentiment = sentiment
                field.language = language_code
                
                db.commit()
                logger.info(f"Updated FormResponseField {field.responsefieldId} with processed data")
            else:
                logger.error(f"FormResponseField not found for formResponseId: {formResponseId}, formfeildId: {formfeildId}")
                
        except Exception as e:
            logger.error(f"Database update failed: {str(e)}")
            db.rollback()
        
        # 5. Process analytics if we have transcribed text
        if transcribed_text:
            try:
                # Get existing analytics for this form
                existing_analytics = db.query(FormAnalytics).filter(
                    FormAnalytics.formId == formId,
                    FormAnalytics.status == "active"
                ).first()
                
                existing_categories = existing_analytics.response_categories if existing_analytics else []
                
                # Process response for analytics
                analytics_result = process_response_for_analytics(
                    transcribed_text, 
                    formId, 
                    existing_categories
                )
                
                # Calculate total responses
                total_responses = sum(cat.get('response_count', 0) for cat in analytics_result["categories"])
                
                # Update or create analytics
                if existing_analytics:
                    existing_analytics.response_categories = analytics_result["categories"]
                    existing_analytics.total_responses = total_responses
                    existing_analytics.update_timestamp = datetime.utcnow()
                    logger.info(f"Updated analytics with {len(analytics_result['categories'])} categories")
                else:
                    new_analytics = FormAnalytics(
                        formId=formId,
                        response_categories=analytics_result["categories"],
                        total_responses=total_responses,
                        status="active"
                    )
                    db.add(new_analytics)
                    logger.info(f"Created new analytics with {len(analytics_result['categories'])} categories")
                
                db.commit()
                logger.info("Analytics processing completed")
                
            except Exception as e:
                logger.error(f"Analytics processing failed: {str(e)}")
                db.rollback()
        
        db.close()
        logger.info(f"Background processing completed for formResponseId: {formResponseId}")
        
    except Exception as e:
        logger.error(f"Background task failed: {str(e)}")
        if 'db' in locals():
            db.close()

def start_background_processing(
    formResponseId: int,
    formId: int,
    formfeildId: int,
    responseText: Optional[str],
    file_content: Optional[bytes],
    file_name: Optional[str],
    file_content_type: Optional[str],
    question_number: int,
    responseTime: Optional[float],
    user_id: str,
    db_session_factory
):
    """Start background processing for a form response field"""
    task_id = f"form_response_{formResponseId}_{formfeildId}_{question_number}"
    
    background_manager.add_task(
        task_id,
        process_form_response_background,
        formResponseId,
        formId,
        formfeildId,
        responseText,
        file_content,
        file_name,
        file_content_type,
        question_number,
        responseTime,
        user_id,
        db_session_factory
    )
    
    logger.info(f"Started background task: {task_id}")
