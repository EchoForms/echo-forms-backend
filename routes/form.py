import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.form import Form
from models.form_fields import FormField
from models.form_response import FormResponse
from models.form_response_field import FormResponseField
from schemas.form import FormCreate, FormUpdate, FormOut
from db import get_db
from middleware.auth import get_current_user
from models.users import User
from sqlalchemy import func, and_, text
from utils.b2 import get_download_authorization, generate_download_url


router = APIRouter(prefix="/forms", tags=["forms"])

@router.post("/", response_model=FormOut)
def create_form(form: FormCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_form = Form(
        title=form.title,
        description=form.description,
        language=form.language,
        status=form.status,
        user_id=current_user.id,
    )
    if form.fields:
        for idx, field in enumerate(form.fields):
            new_field = FormField(
                question=field.question,
                required=field.required,
                options=field.options,
                status=field.status or "active",
                question_number=field.question_number if field.question_number is not None else idx + 1,
                user_id=current_user.id,  # Add user_id to form fields
            )
            new_form.fields.append(new_field)
    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

@router.get("/", response_model=None)
def get_forms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get all forms for the user, not deleted
    forms = db.query(Form).filter(Form.user_id == current_user.id, Form.status != "deleted").all()
    # Sort forms by status='active' first
    forms_sorted = sorted(forms, key=lambda f: f.status != "active")
    # Total forms
    total_forms = len(forms)
    # Active forms
    active_forms = [f for f in forms if f.status == "active"]
    
    # Get all response fields for the user
    form_ids = [f.id for f in forms]
    all_response_fields = db.query(FormResponseField).filter(FormResponseField.user_id == current_user.id).all()
    
    # Query form_responses by user_id - get both total and completed counts
    total_responses = db.query(FormResponse).filter(FormResponse.user_id == current_user.id).count()
    completed_responses = db.query(FormResponse).filter(
        FormResponse.user_id == current_user.id,
        FormResponse.status == "completed"
    ).count()
    print(total_responses, completed_responses)
    # Calculate completion rate
    completion_rate = round((completed_responses / total_responses * 100), 2) if total_responses > 0 else 0
    
    # Calculate average response time
    response_times = [field.response_time for field in all_response_fields if field.response_time is not None]
    avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
    
    return {
        "forms": forms_sorted,
        "total_forms": total_forms,
        "total_responses": completed_responses,
        "active_forms": len(active_forms),
        "completion_rate": completion_rate,
        "avg_response_time": avg_response_time
    }

@router.get("/public/{form_unique_id}", response_model=FormOut)
def get_form_by_unique_id(form_unique_id: str, db: Session = Depends(get_db)):
    form = db.query(Form).filter(Form.form_unique_id == form_unique_id, Form.status != "deleted").first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    # Order fields by question_number
    form.fields.sort(key=lambda f: f.question_number)
    return form

@router.get("/{form_id}", response_model=FormOut)
def get_form(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id, Form.status != "deleted").first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return form

@router.put("/{form_id}", response_model=FormOut)
def update_form(form_id: int, form: FormUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    for key, value in form.dict(exclude_unset=True).items():
        setattr(db_form, key, value)
    db.commit()
    db.refresh(db_form)
    return db_form

@router.delete("/{form_id}")
def delete_form(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not db_form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Set status to deleted instead of actually deleting
    db_form.status = "deleted"
    db.commit()
    return {"detail": "Form deleted"}

@router.get("/{form_id}/results", response_model=None)
def get_form_results(form_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get form results and analytics for the results page"""
    # Verify form ownership
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id, Form.status != "deleted").first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Get all responses for this form (both completed and in-progress)
    all_responses = db.query(FormResponse).filter(
        FormResponse.formId == form_id
    ).all()
    
    # Get completed responses only
    completed_responses = [r for r in all_responses if r.status == "completed"]
    
    # Get all response fields for completed responses
    response_ids = [r.responseId for r in completed_responses]
    all_response_fields = db.query(FormResponseField).filter(
        FormResponseField.formResponseId.in_(response_ids)
    ).all()
    
    # Calculate analytics
    total_responses = len(all_responses)  # All responses (completed + in-progress)
    completed_count = len(completed_responses)  # Only completed responses
    
    # Calculate average response time
    response_times = [field.response_time for field in all_response_fields if field.response_time is not None]
    avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
    
    # Calculate completion rate (completed responses / total responses)
    completion_rate = round((completed_count / total_responses * 100), 2) if total_responses > 0 else 0
    
    # Get question-wise breakdown
    question_breakdown = []
    if form.fields:
        for field in form.fields:
            field_responses = [f for f in all_response_fields if f.formfeildId == field.id]
            question_breakdown.append({
                "question_id": field.id,
                "question_text": field.question,
                "response_count": len(field_responses),
                "percentage": round((len(field_responses) / completed_count * 100), 2) if completed_count > 0 else 0
            })
    
    # Get completion funnel
    completion_funnel = []
    if form.fields:
        total_questions = len(form.fields)
        for i in range(total_questions):
            question_num = i + 1
            responses_at_question = 0
            for response in completed_responses:
                response_fields = [f for f in all_response_fields if f.formResponseId == response.responseId]
                if len(response_fields) >= question_num:
                    responses_at_question += 1
            
            completion_funnel.append({
                "question": f"Q{question_num}",
                "responses": responses_at_question,
                "percentage": round((responses_at_question / completed_count * 100), 2) if completed_count > 0 else 0
            })
    
    # Get analytics data
    from models.form_analytics import FormAnalytics
    analytics = db.query(FormAnalytics).filter(
        FormAnalytics.formId == form_id,
        FormAnalytics.status == "active"
    ).first()
    
    # Also try without status filter in case status is not set
    if not analytics:
        analytics = db.query(FormAnalytics).filter(
            FormAnalytics.formId == form_id
        ).first()
    
    # Prepare analytics data
    analytics_data = {
        "categories": [],
        "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
        "total_categories": 0
    }
    
    if analytics and analytics.response_categories:
        analytics_data["categories"] = analytics.response_categories
        analytics_data["total_categories"] = len(analytics.response_categories)
        
        # Calculate sentiment distribution based on response counts
        for category in analytics.response_categories:
            sentiment = category.get("sentiment", "neutral")
            response_count = category.get("response_count", 0)
            if sentiment in analytics_data["sentiment_distribution"]:
                analytics_data["sentiment_distribution"][sentiment] += response_count

    return {
        "form_id": form.id,
        "form_unique_id": form.form_unique_id,
        "title": form.title,
        "description": form.description,
        "language": form.language,
        "created_at": form.created_at,
        "total_responses": total_responses,
        "completed_responses": completed_count,
        "avg_response_time": avg_response_time,
        "completion_rate": completion_rate,
        "question_breakdown": question_breakdown,
        "completion_funnel": completion_funnel,
        "analytics": analytics_data
    }

@router.get("/{form_id}/responses", response_model=None)
def get_form_responses_paginated(
    form_id: int, 
    page: int = 1, 
    limit: int = 10,
    question_filter: str = None,
    search: str = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    # Verify form ownership
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id, Form.status != "deleted").first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Get completed responses with pagination
    offset = (page - 1) * limit
    
    # Base query for completed responses
    base_query = db.query(FormResponse).filter(
        FormResponse.formId == form_id,
    )
    
    # Apply search filter if provided
    if search:
        # Search in response fields text
        search_query = f"%{search}%"
        response_ids_with_search = db.query(FormResponseField.formResponseId).filter(
            FormResponseField.formId == form_id,
            FormResponseField.responseText.ilike(search_query)
        ).distinct()
        base_query = base_query.filter(FormResponse.responseId.in_(response_ids_with_search))
    
    # Get total count for pagination
    total_count = base_query.count()
    
    # Get paginated responses
    responses = base_query.offset(offset).limit(limit).all()
    
    # Get response fields for these responses
    response_ids = [r.responseId for r in responses]
    response_fields = db.query(FormResponseField).filter(
        FormResponseField.formResponseId.in_(response_ids)
    ).all()
    
    # Group responses by user/response
    formatted_responses = []
    for response in responses:
        user_response_fields = [f for f in response_fields if f.formResponseId == response.responseId]
        
        # Apply question filter if provided
        if question_filter and question_filter != "all":
            user_response_fields = [f for f in user_response_fields if str(f.formfeildId) == question_filter]
        
        if user_response_fields:  # Only include if there are fields to show
            # Generate download URLs for voice files
            file_prefix = f"{form.user_id}/{form.id}/responses/{response.responseId}/"
            auth_token = get_download_authorization(file_prefix, 86400)
            
            formatted_responses.append({
                "response_id": response.responseId,
                "user_id": f"User #{response.responseId}",
                "start_timestamp": response.created_at,
                "language": response.language or "en",
                "responses": [
                    {
                        "question_id": field.formfeildId,
                        "question_text": next((f.question for f in form.fields if f.id == field.formfeildId), "Unknown Question"),
                        "transcript": field.responseText or "No text response",
                        "transcribed_text": field.transcribed_text or "No AI transcription available",
                        "translated_text": field.translated_text,
                        "categories": field.categories or [],
                        "response_time": field.response_time,  # Raw response time for duration calculation
                        "duration": f"{field.response_time:.1f}s" if field.response_time else "0s",
                        "voice_file": generate_download_url(field.voiceFileLink, auth_token) if field.voiceFileLink else None,
                        "sentiment": getattr(field, 'sentiment', 'neutral') or "neutral",
                        "language": getattr(field, 'language', 'en') or "en"
                    }
                    for field in user_response_fields
                ]
            })
    
    return {
        "responses": formatted_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": (total_count + limit - 1) // limit
        }
    }