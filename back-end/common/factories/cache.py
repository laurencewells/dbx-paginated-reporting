"""
Cache factory for creating and managing an in-memory async cache.

Uses aiocache with SimpleMemoryCache backend. Provides a singleton cache
instance shared across the application, with a ``cached`` decorator for
transparent cache-aside on async methods.
"""

import asyncio
import functools
import inspect
from typing import Any, Callable, TypeVar

from aiocache import SimpleMemoryCache
from common.logger import log as L

DEFAULT_TTL = 300  # 5 minutes
DEFAULT_RETRIES = 3

T = TypeVar("T")


class CacheFactory:
    """
    Factory class for creating and managing the application cache.

    Wraps aiocache's SimpleMemoryCache with a clean interface for
    keyed caching, lifecycle management, and a ``cached`` decorator.
    """

    def __init__(self, ttl: int = DEFAULT_TTL, namespace: str = "main"):
        self._ttl = ttl
        self._namespace = namespace
        self._cache: SimpleMemoryCache | None = None

    @property
    def cache(self) -> SimpleMemoryCache:
        if self._cache is None:
            self._cache = SimpleMemoryCache(
                ttl=self._ttl,
                namespace=self._namespace,
            )
        return self._cache

    # -- core operations ------------------------------------------------

    async def get(self, key: str) -> Any:
        return await self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self.cache.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        await self.cache.delete(key)

    async def clear(self, namespace: str | None = None) -> None:
        await self.cache.clear(namespace=namespace)

    # -- write modes ----------------------------------------------------

    def set_fire_and_forget(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Schedule a cache write without blocking the caller."""
        task = asyncio.create_task(self.set(key, value, ttl=ttl))
        task.add_done_callback(self._log_task_error)

    async def set_reliable(
        self, key: str, value: Any, ttl: int | None = None, retries: int = DEFAULT_RETRIES,
    ) -> None:
        """Await a cache write, retrying with exponential back-off on failure."""
        for attempt in range(1, retries + 1):
            try:
                await self.set(key, value, ttl=ttl)
                return
            except Exception:
                if attempt == retries:
                    L.error("Cache set_reliable failed after %d attempts for key=%s", retries, key)
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    # -- decorator ------------------------------------------------------

    def cached(
        self,
        key_template: str,
        *,
        ttl: int | None = None,
        reliable: bool = False,
    ) -> Callable:
        """
        Decorator that adds cache-aside behaviour to an async method.

        ``key_template`` is a format string resolved against the decorated
        function's bound arguments (excluding ``self``).

        Examples::

            @app_cache.cached("suppliers:all")
            async def get_all_suppliers(self) -> list[Supplier]: ...

            @app_cache.cached("suppliers:lakebase:{supplier_id}")
            async def get_by_id(self, supplier_id: int) -> Supplier | None: ...
        """
        def decorator(fn: Callable[..., T]) -> Callable[..., T]:
            sig = inspect.signature(fn)

            @functools.wraps(fn)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                key_args = {k: v for k, v in bound.arguments.items() if k != "self"}
                cache_key = key_template.format_map(key_args)

                hit = await self.get(cache_key)
                if hit is not None:
                    L.debug("Cache HIT  %s", cache_key)
                    return hit

                L.debug("Cache MISS %s", cache_key)
                result = await fn(*args, **kwargs)

                if result is not None:
                    if reliable:
                        await self.set_reliable(cache_key, result, ttl=ttl)
                    else:
                        self.set_fire_and_forget(cache_key, result, ttl=ttl)

                return result

            return wrapper
        return decorator

    # -- lifecycle ------------------------------------------------------

    async def shutdown(self) -> None:
        if self._cache is not None:
            await self._cache.clear()
            L.info("Cache cleared during shutdown")

    # -- internal -------------------------------------------------------

    @staticmethod
    def _log_task_error(task: asyncio.Task) -> None:
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            L.error("Fire-and-forget cache write failed: %s", exc)


app_cache = CacheFactory()
