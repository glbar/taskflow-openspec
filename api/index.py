import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

load_dotenv()

from .database import engine
from . import models
from .routers import auth, teams, tasks, messages


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TaskFlow API", lifespan=lifespan)

# CORS
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5500,http://localhost:8000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized error response
@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "서버 오류가 발생했습니다"}},
    )


# Routers
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(messages.router)

# Vercel serverless handler
handler = Mangum(app, lifespan="off")
