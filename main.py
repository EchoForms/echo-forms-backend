import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from models import Base
from routes.users import router as users_router
from routes.form import router as form_router
from routes.form_response import router as form_response_router
from routes.form_response_field import router as form_response_field_router
from routes.form_analytics import router as form_analytics_router
from db import engine
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "super-secret-session-key"),
)

app.include_router(users_router)
app.include_router(form_router)
app.include_router(form_response_router)
app.include_router(form_response_field_router)
app.include_router(form_analytics_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)} 