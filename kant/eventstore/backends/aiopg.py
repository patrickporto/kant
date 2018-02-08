from collections import namedtuple
from asyncio_extras.contextmanager import async_contextmanager
from async_generator import yield_, async_generator
import aiopg
from kant.projections import ProjectionManager
from ..exceptions import (StreamDoesNotExist, VersionError)
from ..stream import EventStream


class EventStoreConnection:
    def __init__(self):
        self.projections = ProjectionManager()

    @classmethod
    async def create(cls, settings):
        self = EventStoreConnection()
        self.settings = settings
        self.pool = settings.get('pool')
        if self.pool is None:
            self.pool = await aiopg.connect(
                user=settings.get('user'),
                password=settings.get('password'),
                database=settings.get('database'),
                host=settings.get('host'),
            )
        return self

    async def create_keyspace(self, keyspace):
        stmt = """
        CREATE TABLE IF NOT EXISTS {keyspace} (
            id varchar(255),
            data jsonb NOT NULL,
            created_at timestamp NOT NULL,
            updated_at timestamp NOT NULL,
            version bigserial NOT NULL
        )
        """.format(keyspace=keyspace)
        async with self.pool.cursor() as cursor:
            await cursor.execute(stmt)

    async def drop_keyspace(self, keyspace):
        stmt = """
        DROP TABLE {keyspace}
        """.format(keyspace=keyspace)
        async with self.pool.cursor() as cursor:
            await cursor.execute(stmt)

    @async_contextmanager
    async def open(self, keyspace):
        async with self.pool.cursor() as cursor:
            await yield_(EventStore(cursor, keyspace, self.projections))


class EventStore:
    def __init__(self, cursor, keyspace, projections):
        self.cursor = cursor
        self.keyspace = keyspace
        self.projections = projections

    async def get_stream(self, stream: str, start: int = 0, backward: bool = False):
        stmt_select = """
        SELECT {keyspace}.data
        FROM {keyspace} WHERE {keyspace}.id = %(id)s
        """.format(keyspace=self.keyspace)
        if backward:
            stmt_select += " AND CAST(data ? '$version' AS INTEGER) <= %(version)s"
        else:
            stmt_select += " AND CAST(data ? '$version' AS INTEGER) >= %(version)s"
        await self.cursor.execute(stmt_select, {
            'id': str(stream),
            'version': start,
        })
        eventstore_stream = await self.cursor.fetchone()
        if not eventstore_stream:
            raise StreamDoesNotExist(stream)
        return EventStream.make(eventstore_stream[0])

    @async_generator
    async def all_streams(self, start: int = 0, end: int = -1):
        stmt_select = """
        SELECT {keyspace}.data
        FROM {keyspace}
        ORDER BY id
        """.format(keyspace=self.keyspace)
        if start > 0:
            stmt_select += " OFFSET {}".format(start)
        if end > -1:
            stmt_select += " LIMIT {}".format(end)
        await self.cursor.execute(stmt_select)
        eventstore = await self.cursor.fetchall()
        for stream in eventstore:
            await yield_(EventStream.make(stream[0]))

    async def append_to_stream(self, stream: str, eventstream: EventStream, on_save=None):
        try:
            stored_eventstream = await self.get_stream(stream)

            if stored_eventstream.current_version > eventstream.initial_version:
                message = "The version '{0}' was expected in '{1}'".format(
                    eventstream.initial_version,
                    stored_eventstream,
                )
                raise VersionError(message)

            stored_eventstream += eventstream

            stmt_update = """
            UPDATE {keyspace} SET data=%(data)s, updated_at=NOW(), version=%(current_version)s
            WHERE id = %(id)s AND version = %(initial_version)s;
            """.format(keyspace=self.keyspace)
            await self.cursor.execute(stmt_update, {
                'id': str(stream),
                'initial_version': stored_eventstream.initial_version,
                'current_version': stored_eventstream.current_version,
                'data': stored_eventstream.json(),
            })
            if self.cursor.rowcount < 1:
                message = "The version '{0}' was expected in '{1}'".format(
                    eventstream.initial_version,
                    stored_eventstream,
                )
                raise VersionError(message)
            await self.projections.notify_update(self.keyspace, stream, stored_eventstream)
            if on_save is not None:
                on_save(stored_eventstream.current_version)
        except StreamDoesNotExist:
            stmt_insert = """
            INSERT INTO {keyspace} (id, version, data, created_at, updated_at)
            VALUES (%(id)s, %(version)s, %(data)s, NOW(), NOW())
            """.format(keyspace=self.keyspace)
            await self.cursor.execute(stmt_insert, {
                'id': str(stream),
                'version': eventstream.current_version,
                'data': eventstream.json(),
            })
            await self.projections.notify_create(self.keyspace, stream, eventstream)
            if on_save is not None:
                on_save(eventstream.current_version)
