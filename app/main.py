from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os

from app.config import settings
from app.routes import budget_router, insights_router, nlu_router, generate_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Personal Finance Chatbot API",
    description="AI-powered personal finance assistant with budget analysis, spending insights, and persona-aware advice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(budget_router, tags=["Budget"])
app.include_router(insights_router, tags=["Insights"])
app.include_router(nlu_router, tags=["NLU"])
app.include_router(generate_router, tags=["Generate"])

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def root():
    """Serve the main frontend page."""
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {
        "message": "Personal Finance Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": settings.app_env
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.models import ModelFactory
    
    client = ModelFactory.get_client()
    
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "model": client.model_name
    }


@app.get("/chat.html")
async def serve_chat():
    """Serve chat page."""
    chat_page = os.path.join(frontend_path, "chat.html")
    if os.path.exists(chat_page):
        return FileResponse(chat_page)
    return {"error": "Page not found"}


@app.get("/budget.html")
async def serve_budget():
    """Serve budget page."""
    budget_page = os.path.join(frontend_path, "budget.html")
    if os.path.exists(budget_page):
        return FileResponse(budget_page)
    return {"error": "Page not found"}


@app.get("/insights.html")
async def serve_insights():
    """Serve insights page."""
    insights_page = os.path.join(frontend_path, "insights.html")
    if os.path.exists(insights_page):
        return FileResponse(insights_page)
    return {"error": "Page not found"}


@app.get("/settings.html")
async def serve_settings():
    """Serve settings page."""
    settings_page = os.path.join(frontend_path, "settings.html")
    if os.path.exists(settings_page):
        return FileResponse(settings_page)
    return {"error": "Page not found"}


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info(f"Starting Personal Finance Chatbot API")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")
    
    # Initialize model client
    from app.models import ModelFactory
    client = ModelFactory.get_client()
    logger.info(f"Using LLM model: {client.model_name}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Personal Finance Chatbot API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "local"
    )
