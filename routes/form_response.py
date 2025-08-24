from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.form_response import FormResponse
from schemas.form_response import FormResponseCreate, FormResponseUpdate, FormResponseOut
from db import get_db
from models.form import Form
from middleware.auth import get_current_user
from models.users import User

router = APIRouter(prefix="/form-responses", tags=["form-responses"])

@router.post("/", response_model=FormResponseOut)
def create_form_response(form_response: FormResponseCreate, db: Session = Depends(get_db)):
    # Get the form to determine the user_id
    form = db.query(Form).filter(Form.id == form_response.formId).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    new_response = FormResponse(
        **form_response.dict(),
        user_id=form.user_id  # Use the form owner's user_id
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    return new_response

@router.get("/", response_model=list[FormResponseOut])
def get_form_responses(db: Session = Depends(get_db)):
    return db.query(FormResponse).all()

@router.get("/by-form/{form_id}", response_model=list[FormResponseOut])
def get_form_responses_by_form_id(form_id: int, db: Session = Depends(get_db)):
    # Get the form to determine the user_id
    form = db.query(Form).filter(Form.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Get responses for this form that are in progress (not completed)
    responses = db.query(FormResponse).filter(
        FormResponse.formId == form_id,
        FormResponse.user_id == form.user_id,
        FormResponse.status != "completed"
    ).all()
    return responses

@router.get("/{response_id}", response_model=FormResponseOut)
def get_form_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(FormResponse).filter(FormResponse.responseId == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="FormResponse not found")
    return response

@router.put("/{response_id}", response_model=FormResponseOut)
def update_form_response(response_id: int, form_response: FormResponseUpdate, db: Session = Depends(get_db)):
    db_response = db.query(FormResponse).filter(FormResponse.responseId == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="FormResponse not found")
    for key, value in form_response.dict(exclude_unset=True).items():
        setattr(db_response, key, value)
    db.commit()
    db.refresh(db_response)
    return db_response

@router.delete("/{response_id}")
def delete_form_response(response_id: int, db: Session = Depends(get_db)):
    db_response = db.query(FormResponse).filter(FormResponse.responseId == response_id).first()
    if not db_response:
        raise HTTPException(status_code=404, detail="FormResponse not found")
    db.delete(db_response)
    db.commit()
    return {"detail": "FormResponse deleted"} 