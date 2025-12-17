from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine, Base
from .auth import router as auth_router
from .data import router as data_router
import os
from dotenv import load_dotenv

load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure REST API - FastAPI (lab)")

# CORS config
allow_origins = os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(data_router)


@app.get("/")
def root():
    return {"msg": "Secure REST API - FastAPI. See /docs for interactive API UI."}
