from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime

class FormAnalytics(Base):
    __tablename__ = "form_analytics"

    analyticsId = Column(Integer, primary_key=True, index=True)
    formId = Column(Integer, ForeignKey("forms.id"), nullable=False)
    response_categories = Column(JSON, nullable=True)
    total_responses = Column(Integer, default=0, nullable=False)
    create_timestamp = Column(DateTime, default=datetime.utcnow)
    update_timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), nullable=False, default="active")

    form = relationship("Form")
