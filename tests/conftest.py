from os import environ
import aiopg
import pytest


@pytest.fixture
async def dbsession():
    conn = await aiopg.connect(
        user=environ.get('DATABASE_USER'),
        password=environ.get('DATABASE_PASSWORD'),
        database=environ.get('DATABASE_DATABASE'),
        host=environ.get('DATABASE_HOST', 'localhost'),
        port=environ.get('DATABASE_PORT', 5432),
    )
    yield conn
    conn.close()
