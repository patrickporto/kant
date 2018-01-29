async def create_table(cursor):
    stmt = """
    CREATE TABLE IF NOT EXISTS event_store (
        id varchar(255),
        data jsonb NOT NULL,
        created_at timestamp NOT NULL,
        updated_at timestamp NOT NULL
    )
    """
    await cursor.execute(stmt)


async def drop_table(cursor):
    stmt = """
    DROP TABLE event_store
    """
    await cursor.execute(stmt)
