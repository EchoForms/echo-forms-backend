from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from models.users import User
from models import Base
from schemas.users import UserCreate, UserUpdate, UserOut
from db import get_db
from passlib.context import CryptContext
from datetime import datetime, timedelta
from middleware.auth import get_current_user
from authlib.integrations.starlette_client import OAuth
from fastapi import Request, Response
import os
from validators.users import validate_user_create
from utils.users import create_access_token

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Google OAuth config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
    },
)

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    validate_user_create(user, db)
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login_user(form_data: dict, db: Session = Depends(get_db)):
    username = form_data.get("username")
    password = form_data.get("password")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if userinfo:
        email = userinfo.get("email")
        name = userinfo.get("name")
    else:
        user_info = await oauth.google.parse_id_token(token)
        email = user_info.get("email")
        name = user_info.get("name")
    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, username=email, name=name, password="google-oauth")
        db.add(user)
        db.commit()
        db.refresh(user)
    access_token = create_access_token({"sub": str(user.id)})
    # Redirect to frontend with token (or set cookie)
    redirect_url = f"{FRONTEND_URL}/oauth-callback?token={access_token}"
    return Response(status_code=302, headers={"Location": redirect_url})

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "subscription": current_user.subscription,
        "status": current_user.status,
    } 