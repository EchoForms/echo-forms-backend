import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from models import Base
from routes.users import router as users_router
from db import engine

app = FastAPI()
app.include_router(users_router)


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