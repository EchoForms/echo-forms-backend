from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.form_analytics import FormAnalytics
from schemas.form_analytics import FormAnalyticsOut, FormAnalyticsCreate, FormAnalyticsUpdate
from db import get_db
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/form-analytics", tags=["form-analytics"])

@router.post("/", response_model=FormAnalyticsOut)
def create_form_analytics(
    analytics_data: FormAnalyticsCreate,
    db: Session = Depends(get_db)
):
    """Create new form analytics entry"""
    new_analytics = FormAnalytics(
        formId=analytics_data.formId,
        response_categories=analytics_data.response_categories,
        status=analytics_data.status or "active"
    )
    db.add(new_analytics)
    db.commit()
    db.refresh(new_analytics)
    return new_analytics

@router.get("/", response_model=List[FormAnalyticsOut])
def get_all_form_analytics(db: Session = Depends(get_db)):
    """Get all form analytics"""
    return db.query(FormAnalytics).all()

@router.get("/form/{form_id}", response_model=Optional[FormAnalyticsOut])
def get_form_analytics(form_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific form"""
    analytics = db.query(FormAnalytics).filter(
        FormAnalytics.formId == form_id,
        FormAnalytics.status == "active"
    ).first()
    
    if not analytics:
        raise HTTPException(
            status_code=404, 
            detail=f"Analytics not found for form ID {form_id}"
        )
    
    return analytics

@router.put("/{analytics_id}", response_model=FormAnalyticsOut)
def update_form_analytics(
    analytics_id: int,
    analytics_update: FormAnalyticsUpdate,
    db: Session = Depends(get_db)
):
    """Update form analytics"""
    db_analytics = db.query(FormAnalytics).filter(FormAnalytics.analyticsId == analytics_id).first()
    
    if not db_analytics:
        raise HTTPException(
            status_code=404, 
            detail="Form analytics not found"
        )
    
    # Update fields
    for key, value in analytics_update.dict(exclude_unset=True).items():
        setattr(db_analytics, key, value)
    
    # Update timestamp
    db_analytics.update_timestamp = datetime.utcnow()
    
    db.commit()
    db.refresh(db_analytics)
    return db_analytics

@router.delete("/{analytics_id}")
def delete_form_analytics(analytics_id: int, db: Session = Depends(get_db)):
    """Soft delete form analytics (set status to inactive)"""
    db_analytics = db.query(FormAnalytics).filter(FormAnalytics.analyticsId == analytics_id).first()
    
    if not db_analytics:
        raise HTTPException(
            status_code=404, 
            detail="Form analytics not found"
        )
    
    # Soft delete
    db_analytics.status = "inactive"
    db_analytics.update_timestamp = datetime.utcnow()
    
    db.commit()
    return {"detail": "Form analytics deleted successfully"}

@router.get("/form/{form_id}/summary", response_model=dict)
def get_form_analytics_summary(form_id: int, db: Session = Depends(get_db)):
    """Get analytics summary for a specific form"""
    analytics = db.query(FormAnalytics).filter(
        FormAnalytics.formId == form_id,
        FormAnalytics.status == "active"
    ).first()
    
    if not analytics:
        raise HTTPException(
            status_code=404, 
            detail=f"Analytics not found for form ID {form_id}"
        )
    
    categories = analytics.response_categories or []
    
    # Calculate summary statistics
    total_categories = len(categories)
    sentiment_counts = {}
    total_responses = 0
    
    for category in categories:
        sentiment = category.get('sentiment', 'neutral')
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        total_responses += 1
    
    # Calculate sentiment percentages
    sentiment_percentages = {}
    for sentiment, count in sentiment_counts.items():
        sentiment_percentages[sentiment] = (count / total_responses * 100) if total_responses > 0 else 0
    
    return {
        "form_id": form_id,
        "total_categories": total_categories,
        "total_responses": total_responses,
        "sentiment_distribution": sentiment_percentages,
        "categories": categories,
        "last_updated": analytics.update_timestamp
    }
