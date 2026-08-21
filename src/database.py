from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session = request.app.state.session_factory()

    try:
        yield session
    finally:
        await session.close()


def get_sqlalchemy_dsn(dsn: str) -> URL:
    url = make_url(dsn)

    return url.set(drivername="postgresql+asyncpg")
