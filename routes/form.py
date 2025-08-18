from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.form import Form
from models.form_fields import FormField
from schemas.form import FormCreate, FormUpdate, FormOut
from db import get_db
from middleware.auth import get_current_user
from models.users import User

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
            )
            new_form.fields.append(new_field)
    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

@router.get("/", response_model=list[FormOut])
def get_forms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Form).filter(Form.user_id == current_user.id, Form.status != "deleted").all()

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
    db.delete(db_form)
    db.commit()
    return {"detail": "Form deleted"} 