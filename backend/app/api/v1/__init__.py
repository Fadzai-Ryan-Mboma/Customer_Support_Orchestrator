"""
API v1 router initialization
"""
from fastapi import APIRouter
from .webhooks import router as webhooks_router
from .tenants import router as tenants_router
from .conversations import router as conversations_router
from .analytics import router as analytics_router
from .health import router as health_router
from .test import router as test_router

router = APIRouter()

# Include sub-routers
router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(test_router, prefix="/test", tags=["test"])