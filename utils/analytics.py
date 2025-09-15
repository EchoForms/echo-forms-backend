import requests
import os
import json
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of text using Gemini API
    
    Args:
        text: Text to analyze
    
    Returns:
        Sentiment: "positive", "negative", or "neutral"
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            return "neutral"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""Analyze the sentiment of the following text and respond with only one word: "positive", "negative", or "neutral".

Text: "{text}"

Respond with only the sentiment word."""
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 10
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        sentiment = parts[0]["text"].strip().lower()
                        if sentiment in ["positive", "negative", "neutral"]:
                            return sentiment
            
            logger.error("Unexpected response format from Gemini API for sentiment analysis")
            return "neutral"
        else:
            logger.error(f"Gemini API error for sentiment analysis: {response.status_code} - {response.text}")
            return "neutral"
            
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return "neutral"

def generate_categories(existing_categories: List[Dict], new_response_text: str) -> Dict[str, Any]:
    """
    Generate or update categories based on existing categories and new response
    
    Args:
        existing_categories: List of existing category dictionaries with 'category_name' and 'summary_text'
        new_response_text: New response text to categorize
    
    Returns:
        Dictionary containing:
        - 'categories': Updated list of categories
        - 'assigned_to': List of category names the response was assigned to
        - 'new_categories': List of new category names created
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            return {
                'categories': existing_categories,
                'assigned_to': [],
                'new_categories': []
            }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Prepare existing categories context
        existing_context = ""
        if existing_categories:
            existing_context = "Existing categories:\n"
            for cat in existing_categories:
                existing_context += f"- {cat['category_name']}: {cat['summary_text']}\n"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""You are an AI assistant that categorizes form responses with SPECIFIC categories. {existing_context}

New response to categorize: "{new_response_text}"

Analyze this response and create SPECIFIC categories. Avoid broad categories like "Product Feedback" - instead create specific ones like "Product Quality - Color Issues", "Product Quality - Size Problems", "Shipping - Delivery Delays", etc.

Respond with a JSON object in this exact format:
{{
    "assigned_to": ["Specific Category Name 1", "Specific Category Name 2"],
    "new_categories": [
        {{
            "category_name": "Specific Category Name",
            "summary_text": "Brief specific summary under 80 chars",
            "sentiment": "positive/negative/neutral"
        }}
    ],
    "updated_categories": [
        {{
            "category_name": "Specific Category Name",
            "summary_text": "Updated specific summary under 80 chars",
            "sentiment": "positive/negative/neutral"
        }}
    ]
}}

Rules:
- Create SPECIFIC categories, not broad ones
- If response mentions multiple issues, create separate categories for each
- Create new categories for new specific issues
- Be granular: "Product Quality - Color Fading" not just "Product Quality"
- Keep summary_text under 80 characters - be concise and specific
"""
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        response_text = parts[0]["text"].strip()
                        
                        # Try to extract JSON from response
                        try:
                            # Find JSON object in response
                            start_idx = response_text.find('{')
                            end_idx = response_text.rfind('}') + 1
                            if start_idx != -1 and end_idx != 0:
                                json_str = response_text[start_idx:end_idx]
                                ai_result = json.loads(json_str)
                                
                                # Process the AI response
                                assigned_to = ai_result.get('assigned_to', [])
                                new_categories = ai_result.get('new_categories', [])
                                updated_categories = ai_result.get('updated_categories', [])
                                
                                # Build final categories list
                                final_categories = []
                                
                                # Add unmodified existing categories
                                for existing_cat in existing_categories:
                                    if existing_cat['category_name'] not in assigned_to:
                                        final_categories.append(existing_cat)
                                
                                # Add updated categories (increment response count)
                                for updated_cat in updated_categories:
                                    summary = updated_cat['summary_text']
                                    if len(summary) > 80:
                                        summary = summary[:77] + "..."
                                    
                                    # Find existing category to get current response count
                                    existing_count = 0
                                    for existing_cat in existing_categories:
                                        if existing_cat['category_name'] == updated_cat['category_name']:
                                            existing_count = existing_cat.get('response_count', 0)
                                            break
                                    
                                    final_categories.append({
                                        'category_name': updated_cat['category_name'],
                                        'summary_text': summary,
                                        'sentiment': updated_cat['sentiment'],
                                        'response_count': existing_count + 1,  # Increment count
                                        'percentage': 0.0  # Will be calculated later
                                    })
                                
                                # Add new categories (response count = 1)
                                for new_cat in new_categories:
                                    summary = new_cat['summary_text']
                                    if len(summary) > 80:
                                        summary = summary[:77] + "..."
                                    final_categories.append({
                                        'category_name': new_cat['category_name'],
                                        'summary_text': summary,
                                        'sentiment': new_cat['sentiment'],
                                        'response_count': 1,  # New category starts with 1 response
                                        'percentage': 0.0  # Will be calculated later
                                    })
                                
                                logger.info(f"AI assigned to: {assigned_to}, created: {[cat['category_name'] for cat in new_categories]}")
                                
                                return {
                                    'categories': final_categories,
                                    'assigned_to': assigned_to,
                                    'new_categories': [cat['category_name'] for cat in new_categories]
                                }
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON from Gemini response: {e}")
                            
            logger.error("Unexpected response format from Gemini API for category generation")
            return {
                'categories': existing_categories,
                'assigned_to': [],
                'new_categories': []
            }
        else:
            logger.error(f"Gemini API error for category generation: {response.status_code} - {response.text}")
            return {
                'categories': existing_categories,
                'assigned_to': [],
                'new_categories': []
            }
            
    except Exception as e:
        logger.error(f"Error generating categories: {str(e)}")
        return {
            'categories': existing_categories,
            'assigned_to': [],
            'new_categories': []
        }

def calculate_category_percentages(categories: List[Dict], total_responses: int) -> List[Dict]:
    """
    Calculate correct percentages for categories based on actual response counts
    
    Args:
        categories: List of category dictionaries with response_count
        total_responses: Total number of responses
    
    Returns:
        List of categories with correct percentages
    """
    if total_responses == 0:
        for category in categories:
            category['percentage'] = 0.0
        return categories
    
    # Calculate raw percentages
    for category in categories:
        response_count = category.get('response_count', 0)
        percentage = (response_count / total_responses) * 100
        category['percentage'] = round(percentage, 2)
    
    # Fix rounding issues by adjusting the last category
    if categories:
        total_percentage = sum(cat['percentage'] for cat in categories)
        if total_percentage != 100.0:
            # Calculate the difference and add it to the last category
            difference = 100.0 - total_percentage
            categories[-1]['percentage'] = round(categories[-1]['percentage'] + difference, 2)
    
    return categories

def process_response_for_analytics(transcribed_text: str, form_id: int, existing_categories: List[Dict] = None) -> Dict[str, Any]:
    """
    Process a transcribed response for analytics
    
    Args:
        transcribed_text: Transcribed text from voice response
        form_id: ID of the form
        existing_categories: Existing categories for this form
    
    Returns:
        Dictionary containing sentiment and updated categories
    """
    try:
        if not transcribed_text or not transcribed_text.strip():
            logger.warning("Empty transcribed text, skipping analytics")
            return {
                "sentiment": "neutral",
                "categories": existing_categories or [],
                "assigned_to": [],
                "new_categories": []
            }
        
        # Analyze sentiment
        sentiment = analyze_sentiment(transcribed_text)
        logger.info(f"Analyzed sentiment: {sentiment}")
        
        # Generate/update categories
        category_result = generate_categories(existing_categories or [], transcribed_text)
        categories = category_result['categories']
        assigned_to = category_result['assigned_to']
        new_categories = category_result['new_categories']
        
        # Calculate total responses and correct percentages
        total_responses = sum(cat.get('response_count', 0) for cat in categories)
        categories_with_percentages = calculate_category_percentages(categories, total_responses)
        
        logger.info(f"Generated {len(categories_with_percentages)} categories")
        logger.info(f"Assigned to: {assigned_to}")
        logger.info(f"New categories: {new_categories}")
        
        return {
            "sentiment": sentiment,
            "categories": categories_with_percentages,
            "assigned_to": assigned_to,
            "new_categories": new_categories
        }
        
    except Exception as e:
        logger.error(f"Error processing response for analytics: {str(e)}")
        return {
            "sentiment": "neutral",
            "categories": existing_categories or [],
            "assigned_to": [],
            "new_categories": []
        }
