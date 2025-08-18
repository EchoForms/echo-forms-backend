from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from . import Base
import random
import string

def generate_short_id(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

class Form(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    form_unique_id = Column(String(12), unique=True, nullable=False, default=generate_short_id)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    # Relationship
    owner = relationship("User", back_populates="forms")
    fields = relationship("FormField", back_populates="form", cascade="all, delete-orphan") 