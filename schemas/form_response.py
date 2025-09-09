from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FormResponseBase(BaseModel):
    formId: int
    status: Optional[str] = "in_progress"
    submitTimestamp: Optional[datetime] = None
    language: Optional[str] = "en"

class FormResponseCreate(FormResponseBase):
    pass

class FormResponseUpdate(BaseModel):
    status: Optional[str]
    submitTimestamp: Optional[datetime]
    language: Optional[str]

class FormResponseOut(FormResponseBase):
    responseId: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 