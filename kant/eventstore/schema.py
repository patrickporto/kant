def create_table(dbsession):
    with dbsession.cursor() as cursor:
        stmt = """
        CREATE TABLE IF NOT EXISTS event_store (
            id varchar(255),
            data json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL
        )
        """
        cursor.execute(stmt)
