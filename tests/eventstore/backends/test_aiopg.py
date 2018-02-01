import pytest
from kant.eventstore.backends.aiopg import EventStoreConnection


@pytest.mark.asyncio
async def test_create_table_should_create_table_if_not_exists(dbsession):
    # arrange
    settings = {
        'pool': dbsession,
    }
    connection = await EventStoreConnection.create(settings)
    # act
    await connection.create_keyspace('event_store')
    # assert
    async with dbsession.cursor() as cursor:
        await cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'event_store'
        );
        """)
        (exists,) = await cursor.fetchone()
        assert exists


@pytest.mark.asyncio
async def test_drop_table_should_drop_table_if_exists(dbsession):
    # arrange
    settings = {
        'pool': dbsession,
    }
    connection = await EventStoreConnection.create(settings)
    await connection.create_keyspace('event_store')
    # act
    await connection.drop_keyspace('event_store')
    # assert
    async with dbsession.cursor() as cursor:
        await cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'event_store'
        );
        """)
        (exists,) = await cursor.fetchone()
        assert not exists
