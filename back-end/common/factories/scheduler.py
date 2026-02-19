from apscheduler.schedulers.asyncio import AsyncIOScheduler

class SchedulerFactory:
    """
    Factory class for creating and configuring the AsyncIOScheduler.
    """
    def __init__(self):
        """Initialize the scheduler factory."""
        self._scheduler = AsyncIOScheduler()

    def create_scheduler(self) -> AsyncIOScheduler:
        """Create and configure the AsyncIOScheduler."""
        return self._scheduler
    
    @property
    def scheduler(self) -> AsyncIOScheduler:
        """Get the created scheduler instance."""
        return self._scheduler

scheduler_factory = SchedulerFactory()