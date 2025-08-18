from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func, JSON
from sqlalchemy.orm import relationship
from . import Base

class FormField(Base):
    __tablename__ = "form_fields"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)
    required = Column(Boolean, default=False)
    form_id = Column(Integer, ForeignKey("forms.id"), nullable=False)
    options = Column(JSON, nullable=True)
    question_number = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    form = relationship("Form", back_populates="fields") 