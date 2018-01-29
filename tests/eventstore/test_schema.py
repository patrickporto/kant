import pytest
from kant.eventstore.schema import create_table, drop_table


@pytest.mark.asyncio
async def test_create_table_should_create_table_if_not_exists(dbsession):
    async with dbsession.cursor() as cursor:
        # act
        await create_table(cursor)
        # assert
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
    async with dbsession.cursor() as cursor:
        # arrange
        await create_table(cursor)
        # act
        await drop_table(cursor)
        # assert
        await cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'event_store'
        );
        """)
        (exists,) = await cursor.fetchone()
        assert not exists
