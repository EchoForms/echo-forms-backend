from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class FormResponseFieldBase(BaseModel):
    formResponseId: int = Field(..., description="ID of the form response")
    formId: int = Field(..., description="ID of the form")
    formfeildId: int = Field(..., description="ID of the form field")
    responseText: Optional[str] = Field(None, description="Text response")
    voiceFileLink: Optional[str] = Field(None, description="Link to voice file")

class FormResponseFieldCreate(FormResponseFieldBase):
    isLastQuestion: Optional[bool] = False

class FormResponseFieldUpdate(BaseModel):
    responseText: Optional[str]
    voiceFileLink: Optional[str]

class FormResponseFieldOut(FormResponseFieldBase):
    responsefieldId: int

    class Config:
        orm_mode = True 