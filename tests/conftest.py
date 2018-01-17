from os import environ
from async_generator import yield_, async_generator
import aiopg
import pytest


@pytest.fixture
@async_generator
async def dbsession():
    conn = await aiopg.connect(
        user=environ.get('DATABASE_USER'),
        password=environ.get('DATABASE_PASSWORD'),
        database=environ.get('DATABASE_DATABASE'),
        host=environ.get('DATABASE_HOST', 'localhost'),
        port=environ.get('DATABASE_PORT', 5432),
    )
    await yield_(conn)
    conn.close()
