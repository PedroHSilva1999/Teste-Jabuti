import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import app.models
from app.api.users import router as users_router
from app.cache import cache_client
from app.config import settings
from app.database import Base, engine


async def wait_for_dependencies(retries: int = 15, delay: int = 2) -> None:
    last_error: Exception | None = None

    for _ in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            cache_client.ping()
            return
        except (OperationalError, RedisError) as exc:
            last_error = exc
            await asyncio.sleep(delay)

    if last_error is not None:
        raise last_error


@asynccontextmanager
async def lifespan(_: FastAPI):
    await wait_for_dependencies()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.include_router(users_router)
