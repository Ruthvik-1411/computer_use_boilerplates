"""FastAPI app entry point for Gemini Computer Use Agent API"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api import routes
from agent.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for a fastapi service"""
    logger.info("Starting Gemini Computer Use API...")
    yield
    logger.info("Shutting down Gemini Computer Use API...")

app = FastAPI(
    title="Gemini Computer Use Agent API",
    version="1.0.0",
    description="API interface to control the Gemini Computer Use Agent.",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to track total process times"""
    start_time = time.perf_counter()
    
    response = await call_next(request)
    
    process_time = time.perf_counter() - start_time
    
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    logger.info(f"{request.method} {request.url.path} processed in {process_time:.3f}s")
    
    return response

app.include_router(routes.router, prefix="/api/v1")
