from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any

class FormResponseFieldBase(BaseModel):
    formResponseId: int = Field(..., description="ID of the form response")
    formId: int = Field(..., description="ID of the form")
    formfeildId: int = Field(..., description="ID of the form field")
    responseText: Optional[str] = Field(None, description="Text response")
    voiceFileLink: Optional[str] = Field(None, description="Link to voice file")
    response_time: Optional[float] = Field(None, description="Response time in seconds")
    transcribed_text: Optional[str] = Field(None, description="Transcribed text from voice file")
    translated_text: Optional[str] = Field(None, description="Translated text to English")
    categories: Optional[List[Dict[str, Any]]] = Field(None, description="Categories assigned to this response")
    sentiment: Optional[str] = Field("neutral", description="Sentiment analysis result: positive, negative, or neutral")
    language: Optional[str] = Field("en", description="Language code of the response field")

class FormResponseFieldCreate(FormResponseFieldBase):
    isLastQuestion: Optional[bool] = False

class FormResponseFieldUpdate(BaseModel):
    responseText: Optional[str]
    voiceFileLink: Optional[str]
    response_time: Optional[float]
    transcribed_text: Optional[str]
    translated_text: Optional[str]
    categories: Optional[List[Dict[str, Any]]]
    sentiment: Optional[str]
    language: Optional[str]

class FormResponseFieldOut(FormResponseFieldBase):
    responsefieldId: int

    class Config:
        from_attributes = True 