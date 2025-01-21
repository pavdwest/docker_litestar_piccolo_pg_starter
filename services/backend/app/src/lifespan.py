from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable
import inspect

from litestar import Litestar

from src.logging.service import logger


ON_INIT = []
def register_on_init(func):
    ON_INIT.append(func)


ON_STARTUP = []
def register_on_startup(func):
    ON_STARTUP.append(func)


MIDDLEWARE = []
def register_middleware(func):
    MIDDLEWARE.append(func)


ON_SHUTDOWN = []
def register_on_shutdown(func):
    ON_SHUTDOWN.append(func)


async def _run_func(func: Callable):
    """Runs a function, either async or sync.

    Args:
        func (Callable): _description_
    """
    await func() if inspect.iscoroutinefunction(func) else func()


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    # Startup
    for startup in ON_STARTUP:
        logger.info(f"Running startup: {startup.__name__}")
        await _run_func(startup)
    yield
    # Shutdown
    for shutdown in ON_SHUTDOWN:
        logger.info(f"Running shutdown: {shutdown.__name__}")
        await _run_func(shutdown)
