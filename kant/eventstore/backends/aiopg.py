from collections import namedtuple
from asyncio_extras.contextmanager import async_contextmanager
from async_generator import yield_
import aiopg
from kant.projections import ProjectionManager
from ..exceptions import (ObjectDoesNotExist, IntegrityError,
                          StreamDoesNotExist, VersionError)
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

    def _get_eventstream(self, stream, event_store, mode):
        if event_store:
            if 'w' in mode and 'r' not in mode:
                raise IntegrityError(stream)
            eventstream = EventStream.make(event_store[0])
        else:
            if 'r' in mode and 'w' not in mode:
                raise ObjectDoesNotExist(stream)
            eventstream = EventStream()
        return eventstream

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
    async def open(self, name, mode='r', skip_version=0, optimistic=True):
        """
        Open stream and return a corresponding EventStream. If the stream cannot be opened, an ObjectDoesNotExist is raised.
        """
        name_splitted = name.split('/')
        if len(name_splitted) != 2:
            raise StreamDoesNotExist(name)
        keyspace = '_'.join(name_splitted[:-1])
        stream = name_splitted[-1]
        async with self.pool.cursor() as cursor:
            async with cursor.begin() as transaction:
                stmt_select = """
                SELECT {keyspace}.data
                FROM {keyspace} WHERE {keyspace}.id = %(id)s AND CAST(data ? '$version' AS INTEGER) >= %(version)s
                """.format(keyspace=keyspace)
                if not optimistic:
                    stmt_select += " FOR UPDATE"
                await cursor.execute(stmt_select, {
                    'id': str(stream),
                    'version': skip_version,
                })
                event_store = await cursor.fetchone()
                eventstream = self._get_eventstream(stream, event_store, mode)

                await yield_(eventstream)

                if not eventstream.exists():
                    stmt_insert = """
                    INSERT INTO {keyspace} (id, version, data, created_at, updated_at)
                    VALUES (%(id)s, %(version)s, %(data)s, NOW(), NOW())
                    """.format(keyspace=keyspace)
                    await cursor.execute(stmt_insert, {
                        'id': str(stream),
                        'version': eventstream.current_version,
                        'data': eventstream.json(),
                    })
                    await self.projections.notify_create(keyspace, stream, eventstream)
                elif eventstream.current_version > eventstream.initial_version:
                    stmt_update = """
                    UPDATE {keyspace} SET data=%(data)s, updated_at=NOW(), version=%(current_version)s
                    WHERE id = %(id)s AND version = %(initial_version)s;
                    """.format(keyspace=keyspace)
                    await cursor.execute(stmt_update, {
                        'id': str(stream),
                        'initial_version': eventstream.initial_version,
                        'current_version': eventstream.current_version,
                        'data': eventstream.json(),
                    })
                    if cursor.rowcount < 1:
                        message = "The expected version is {expected_version}".format(
                            expected_version=eventstream.initial_version,
                        )
                        raise VersionError(message)
                    await self.projections.notify_update(keyspace, stream, eventstream)
