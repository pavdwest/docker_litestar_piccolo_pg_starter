
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable
import inspect

from litestar import Litestar

from src.logging.service import logger


_ON_STARTUP = []
def register_on_startup(func):
    _ON_STARTUP.append(func)
    return func


_ON_SHUTDOWN = []
def register_on_shutdown(func):
    _ON_SHUTDOWN.append(func)
    return func


async def _run_func(func: Callable):
    await func() if inspect.iscoroutinefunction(func) else func()


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    # Startup
    for startup in _ON_STARTUP:
        logger.info(f"Running startup: {startup.__name__}")
        await _run_func(startup)
    yield
    for shutdown in _ON_SHUTDOWN:
        logger.info(f"Running shutdown: {shutdown.__name__}")
        await _run_func(shutdown)
