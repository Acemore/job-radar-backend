from sqlalchemy.engine import URL

from src.database import get_sqlalchemy_dsn


def test_get_sqlalchemy_dsn():
    dsn = "postgresql://postgres:password@localhost:5432/mydatabase"

    sqlalchemy_dsn = get_sqlalchemy_dsn(dsn)

    assert isinstance(sqlalchemy_dsn, URL)
    assert sqlalchemy_dsn.drivername == "postgresql+asyncpg"
