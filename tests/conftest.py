from os import environ
import psycopg2
import pytest


@pytest.fixture
async def dbsession():
    conn = psycopg2.connect(
        user=environ.get('DATABASE_USER'),
        password=environ.get('DATABASE_PASSWORD'),
        dbname=environ.get('DATABASE_DATABASE'),
        host=environ.get('DATABASE_HOST', 'localhost'),
        port=environ.get('DATABASE_PORT', 5432),
    )
    yield conn
    conn.close()
