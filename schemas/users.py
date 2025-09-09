from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: Optional[str] = None
    username: str
    email: EmailStr
    role: Optional[str] = "user"
    subscription: Optional[str] = "free"
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    role: Optional[str]
    subscription: Optional[str]
    status: Optional[str]

class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 