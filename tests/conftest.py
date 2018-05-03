from os import environ

import aiopg
from aiopg.sa import create_engine
from async_generator import async_generator, yield_
from kant.eventstore.connection import connect

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


@pytest.fixture
@async_generator
async def saconnection():
    engine = await create_engine(
        user=environ.get('DATABASE_USER'),
        password=environ.get('DATABASE_PASSWORD'),
        database=environ.get('DATABASE_DATABASE'),
        host=environ.get('DATABASE_HOST', 'localhost'),
        port=environ.get('DATABASE_PORT', 5432),
    )
    async with engine.acquire() as conn:
        async with conn.begin() as transaction:
            await yield_(conn)
            await transaction.rollback()


@pytest.fixture
@async_generator
async def eventsourcing(dbsession):
    eventstore = await connect(
        pool=dbsession,
    )
    await eventstore.create_keyspace('event_store')
    await yield_(eventstore)
    await eventstore.drop_keyspace('event_store')
    await eventstore.close()
