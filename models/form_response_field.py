from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from . import Base

class FormResponseField(Base):
    __tablename__ = "form_response_fields"

    responsefieldId = Column(Integer, primary_key=True, index=True)
    formResponseId = Column(Integer, ForeignKey("form_responses.responseId"), nullable=False)
    formId = Column(Integer, ForeignKey("forms.id"), nullable=False)
    formfeildId = Column(Integer, ForeignKey("form_fields.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    responseText = Column(Text, nullable=True)
    voiceFileLink = Column(String(255), nullable=True)
    response_time = Column(Float, nullable=True)
    transcribed_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)
    categories = Column(JSON, nullable=True)
    sentiment = Column(String(20), nullable=True, default="neutral")
    language = Column(String(10), nullable=True, default="en")

    form_response = relationship("FormResponse")
    form_field = relationship("FormField")
    form = relationship("Form")
    user = relationship("User") 