from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from . import Base

class FormResponse(Base):
    __tablename__ = "form_responses"

    responseId = Column(Integer, primary_key=True, index=True)
    formId = Column(Integer, ForeignKey("forms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    status = Column(String(32), nullable=False, default="in_progress")
    submitTimestamp = Column(TIMESTAMP, nullable=True)
    language = Column(String(10), nullable=True, default="en")

    form = relationship("Form")
    user = relationship("User") 