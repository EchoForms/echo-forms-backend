from fastapi import HTTPException, Depends
from models.users import User
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db import get_db


def validate_user_create(data, db):
    if not data.name or not data.name.strip():
        raise HTTPException(status_code=422, detail="Name must not be empty.")
    db_user = db.query(User).filter(User.username == data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered") 
    db_user = db.query(User).filter(User.email == data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered") 
    if not data.password:
        raise HTTPException(status_code=422, detail="Password must not be empty.")
    if len(data.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters long.")