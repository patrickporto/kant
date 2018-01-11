from collections.abc import MutableMapping


class EventStream(object):
    def __init__(self, row):
        self._row = row


class StreamManager(MutableMapping):
    db_table = 'event_store'

    def __init__(self, session):
        self._session = session

    async def __getitem__(self, key):
        async with self._session.cursor() as cursor:
            stmt = """
            SELECT * FROM event_store WHERE id = %(id)s;
            """
            await cursor.execute(stmt, {
                'id': key,
            })
            return EventStream(await cursor.fetchone())

    def __delitem__(self, key):
        with self._session.cursor() as cursor:
            stmt = """
            DELETE FROM event_store WHERE id = %(id)s;
            """
            cursor.execute(stmt, {
                'id': key,
            })

    def __iter__(self):
        with self._session.cursor() as cursor:
            stmt = """
            SELECT * FROM event_store;
            """
            cursor.execute(stmt)
            return cursor.fetchone()

    def __len__(self):
        with self._session.cursor() as cursor:
            stmt = """
            SELECT count(*) FROM event_store;
            """
            cursor.execute(stmt)
            (count,) = cursor.fetchone()
            return count

    def __setitem__(self, key, value):
        with self._session.cursor() as cursor:
            stmt = """
            UPDATE event_store SET data=%(data)s updated_at=NOW() WHERE id = %(id)s;
            INSERT INTO event_store (id, data, created_at, updated_at)
                SELECT %(id)s, %(data)s, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM table WHERE id = %(id)s);
            """
            cursor.execute(stmt, {
                'id': key,
            })
            (count,) = cursor.fetchone()
            return count
