def create_table(dbsession):
    with dbsession.cursor() as cursor:
        stmt = """
        CREATE TABLE event_store (
            id varchar(255),
            data json NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL
        )
        """
        cursor.execute(stmt)


def drop_table(dbsession):
    with dbsession.cursor() as cursor:
        stmt = """
        DROP TABLE event_store
        """
        cursor.execute(stmt)
