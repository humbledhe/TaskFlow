from fastapi import FastAPI, Request
from redis.asyncio import Redis

from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )

    app.state.redis = redis_client

    try:
        await redis_client.ping()
        yield
    finally:
        try:
            await redis_client.aclose()
        finally:
            await engine.dispose()
