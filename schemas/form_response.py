from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FormResponseBase(BaseModel):
    formId: int
    status: Optional[str] = "in_progress"
    submitTimestamp: Optional[datetime] = None

class FormResponseCreate(FormResponseBase):
    pass

class FormResponseUpdate(BaseModel):
    status: Optional[str]
    submitTimestamp: Optional[datetime]

class FormResponseOut(FormResponseBase):
    responseId: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 