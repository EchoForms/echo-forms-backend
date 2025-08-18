from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class FormFieldBase(BaseModel):
    question: str
    required: bool = False
    options: Optional[Any] = None
    status: Optional[str] = "active"
    question_number: Optional[int] = 1

class FormFieldCreate(FormFieldBase):
    pass

class FormFieldOut(FormFieldBase):
    id: int
    form_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 