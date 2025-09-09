from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form as FastAPIForm
from sqlalchemy.orm import Session
from models.form_response_field import FormResponseField
from models.form_response import FormResponse
from schemas.form_response_field import FormResponseFieldCreate, FormResponseFieldUpdate, FormResponseFieldOut
from db import get_db, SessionLocal
from datetime import datetime
from utils.b2 import get_download_authorization, generate_download_url
from utils.background_tasks import start_background_processing
from typing import Optional
from models.form import Form

router = APIRouter(prefix="/form-response-fields", tags=["form-response-fields"])

@router.post("/", response_model=FormResponseFieldOut)
async def create_form_response_field(
    formResponseId: int = FastAPIForm(...),
    formId: int = FastAPIForm(...),
    formfeildId: int = FastAPIForm(...),
    question_number: int = FastAPIForm(...), # Used for file naming only, not stored in DB
    responseText: Optional[str] = FastAPIForm(None),
    isLastQuestion: Optional[bool] = FastAPIForm(False),
    responseTime: Optional[float] = FastAPIForm(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if not formResponseId or not formfeildId:
        raise HTTPException(status_code=400, detail="formResponseId and formfeildId are required.")

    # Get the form to determine the user_id
    form = db.query(Form).filter(Form.id == formId).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    form_response_obj = db.query(FormResponse).filter(FormResponse.responseId == formResponseId).first()

    if not form_response_obj:
        raise HTTPException(status_code=404, detail="FormResponse not found")

    if form_response_obj.status == "completed":
        raise HTTPException(status_code=400, detail="FormResponse is already completed")

    # Prepare file data for background processing
    file_content = None
    file_name = None
    file_content_type = None
    
    if file:
        user_id = form.user_id if form else "unknown"
        file_ext = file.filename.split('.')[-1]
        file_name = f"{user_id}/{formId}/responses/{formResponseId}/{question_number}.{file_ext}"
        file_content = await file.read()
        file_content_type = file.content_type

    # Create the initial database record immediately (without processed data)
    new_field = FormResponseField(
        formResponseId=formResponseId,
        formId=formId,
        formfeildId=formfeildId,
        responseText=responseText,
        voiceFileLink=None,  # Will be updated by background task
        response_time=responseTime,
        transcribed_text=None,  # Will be updated by background task
        translated_text=None,  # Will be updated by background task
        categories=None,  # Will be updated by background task
        sentiment="neutral",  # Will be updated by background task
        language="en",  # Will be updated by background task
        user_id=form.user_id
    )
    db.add(new_field)

    # Mark form as completed if this is the last question
    if isLastQuestion:
        form_response_obj.status = "completed"
        form_response_obj.submitTimestamp = datetime.utcnow()

    # Commit the initial record immediately
    db.commit()
    db.refresh(new_field)

    # Start background processing for heavy operations
    if file_content or responseText:
        start_background_processing(
            formResponseId=formResponseId,
            formId=formId,
            formfeildId=formfeildId,
            responseText=responseText,
            file_content=file_content,
            file_name=file_name,
            file_content_type=file_content_type,
            question_number=question_number,
            responseTime=responseTime,
            user_id=form.user_id,
            db_session_factory=SessionLocal
        )

    # Return the initial record immediately (without processed data)
    return new_field

@router.get("/", response_model=list[FormResponseFieldOut])
def get_form_response_fields(db: Session = Depends(get_db)):
    return db.query(FormResponseField).all()

@router.get("/by-response/{form_response_id}", response_model=list[FormResponseFieldOut])
def get_form_response_fields_by_response_id(form_response_id: int, db: Session = Depends(get_db)):
    fields = db.query(FormResponseField).filter(FormResponseField.formResponseId == form_response_id).all()
    if not fields:
        return []

    form_response_obj = db.query(FormResponse).filter(FormResponse.responseId == form_response_id).first()
    form_id = form_response_obj.formId
    form_obj = db.query(Form).filter(Form.id == form_id).first()
    
    file_prefix = f"{form_obj.user_id}/{form_id}/responses/{form_response_id}/"
    
    auth_token = get_download_authorization(file_prefix, 86400)
    print(f"Authorization Token: {auth_token}")
    
    # Process each field to get fresh download URLs for voice files
    for field in fields:
        if field.voiceFileLink:
            field.voiceFileLink = generate_download_url(field.voiceFileLink, auth_token)
    
    return fields

@router.get("/{responsefield_id}", response_model=FormResponseFieldOut)
def get_form_response_field(responsefield_id: int, db: Session = Depends(get_db)):
    field = db.query(FormResponseField).filter(FormResponseField.responsefieldId == responsefield_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="FormResponseField not found")
    return field

@router.put("/{responsefield_id}", response_model=FormResponseFieldOut)
def update_form_response_field(responsefield_id: int, field_update: FormResponseFieldUpdate, db: Session = Depends(get_db)):
    db_field = db.query(FormResponseField).filter(FormResponseField.responsefieldId == responsefield_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="FormResponseField not found")
    for key, value in field_update.dict(exclude_unset=True).items():
        setattr(db_field, key, value)
    db.commit()
    db.refresh(db_field)
    return db_field

@router.delete("/{responsefield_id}")
def delete_form_response_field(responsefield_id: int, db: Session = Depends(get_db)):
    db_field = db.query(FormResponseField).filter(FormResponseField.responsefieldId == responsefield_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="FormResponseField not found")
    db.delete(db_field)
    db.commit()
    return {"detail": "FormResponseField deleted"} 