"""Routes package."""
from app.routes.budget import router as budget_router
from app.routes.insights import router as insights_router
from app.routes.nlu import router as nlu_router
from app.routes.generate import router as generate_router

__all__ = ["budget_router", "insights_router", "nlu_router", "generate_router"]
