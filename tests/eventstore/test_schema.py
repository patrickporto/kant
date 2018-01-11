import pytest
from kant.eventstore.schema import create_table, drop_table


@pytest.mark.asyncio
async def test_create_table_should_create_table_if_not_exists(dbsession):
    # act
    await create_table(dbsession)
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
    await create_table(dbsession)
    # act
    await drop_table(dbsession)
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
