from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .databasehealthcheck import router as databasehealthcheck_router
from .me import router as me_router
from .agent import router as agent_router
from .structures import router as structures_router
from .templates import router as templates_router
from .discovery import router as discovery_router
from .projects import router as projects_router
from .images import router as images_router

router = APIRouter()

router.include_router(healthcheck_router)
router.include_router(databasehealthcheck_router)
router.include_router(me_router)
router.include_router(agent_router)
router.include_router(projects_router)
router.include_router(structures_router)
router.include_router(templates_router)
router.include_router(discovery_router)
router.include_router(images_router)
