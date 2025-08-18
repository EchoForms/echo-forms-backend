from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .form_fields import FormFieldCreate, FormFieldOut

class FormBase(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = "draft"

class FormCreate(FormBase):
    fields: Optional[List[FormFieldCreate]] = None

class FormUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    language: Optional[str]
    status: Optional[str]

class FormOut(BaseModel):
    id: int
    form_unique_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    title: str
    description: Optional[str]
    language: Optional[str]
    status: Optional[str]
    fields: Optional[List[FormFieldOut]] = None

    class Config:
        orm_mode = True 