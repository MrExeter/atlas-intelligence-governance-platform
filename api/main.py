import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, research
from api.middleware.logging import logging_middleware

ENV = os.getenv("ENV", "development")

# App config (unchanged)
if ENV == "production":
    app = FastAPI(
        title="Atlas Intelligence Agent",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
else:
    app = FastAPI(title="Atlas Intelligence Agent")

# CORS config (replace your wildcard block with this)
if ENV == "production":
    allowed_origins = [
        "https://atlas.commandercoconut.com",
    ]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware + routes (unchanged)
app.middleware("http")(logging_middleware)
app.include_router(health.router)
app.include_router(research.router)