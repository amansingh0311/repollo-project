from fastapi.responses import JSONResponse
from fastapi import APIRouter

from .research import research_router
from .moderation import moderation_router


api_router = APIRouter(
    redirect_slashes=True,
)

# Include research agent routes
api_router.include_router(research_router)

# Include content moderation routes
api_router.include_router(moderation_router)



