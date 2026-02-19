"""
Application factory for creating and configuring the FastAPI application.

This module provides a clean separation between application creation,
configuration loading, and setup logic. No module-level singletons are
created here; the entry point (app.py) instantiates AppFactory at runtime
after environment variables have been loaded.
"""
from common.logger import log as L
from contextlib import asynccontextmanager
from typing import Optional
from common.factories.scheduler import scheduler_factory
from common.factories.lakebase import LakebaseFactory
from common.factories.cache import app_cache
from fastapi import FastAPI


class AppFactory:
    """
    Factory class for creating and configuring the FastAPI application.

    Env-dependent components (LakebaseFactory) are created at runtime
    inside the lifespan, not at import time.
    """

    def __init__(self):
        self.scheduler = scheduler_factory.scheduler
        self._app: Optional[FastAPI] = None
        self._lakebase: Optional[LakebaseFactory] = None

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        FastAPI lifespan context manager for startup and shutdown.

        Creates env-dependent factories here so nothing touches
        environment variables at import time.
        """
        try:
            L.info("Starting application setup...")

            self.scheduler.start()
            L.info("Scheduler started")

            self._lakebase = LakebaseFactory()
            await self._lakebase.initialize()

            yield

        except Exception as e:
            L.error(f"Error during startup: {str(e)}")
            raise
        finally:
            L.info("Starting application shutdown...")

            if self._lakebase:
                await self._lakebase.shutdown()

            await app_cache.shutdown()

            if self.scheduler.running:
                self.scheduler.shutdown()
                L.info("Scheduler shutdown")

            L.info("Application shutdown complete")

    def create_app(self) -> FastAPI:
        """
        Create and configure the FastAPI application.

        Returns:
            FastAPI: The configured application instance
        """
        app = FastAPI(lifespan=self.lifespan)
        self._app = app
        L.info("FastAPI application created")
        return app

    @property
    def app(self) -> FastAPI:
        if self._app is None:
            raise RuntimeError("App not created yet. Call create_app() first.")
        return self._app
