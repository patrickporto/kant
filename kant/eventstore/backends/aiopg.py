from collections import namedtuple
from copy import deepcopy
from asyncio_extras.contextmanager import async_contextmanager
from async_generator import yield_
import aiopg
from ..exceptions import ObjectDoesNotExist, IntegrityError, StreamDoesNotExist
from ..stream import EventStream


class EventStoreConnection:

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
            updated_at timestamp NOT NULL
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
    async def open(self, name, mode='r', skip_version=0):
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
                FOR UPDATE
                """.format(keyspace=keyspace)
                await cursor.execute(stmt_select, {
                    'id': str(stream),
                    'version': skip_version,
                })
                event_store = await cursor.fetchone()
                eventstream = self._get_eventstream(stream, event_store, mode)

                old_eventstream = deepcopy(eventstream)

                await yield_(eventstream)

                if not eventstream.exists():
                    stmt_insert = """
                    INSERT INTO {keyspace} (id, data, created_at, updated_at)
                    VALUES (%(id)s, %(data)s, NOW(), NOW())
                    """.format(keyspace=keyspace)
                    await cursor.execute(stmt_insert, {
                        'id': str(stream),
                        'data': eventstream.decode(),
                    })
                elif eventstream > old_eventstream:
                    message = "The version is {current_version}, but the expected is {expected_version}".format(
                        current_version=eventstream.initial_version,
                        expected_version=events.initial_version,
                    )
                    raise VersionError(message)
                elif eventstream.current_version > old_eventstream.initial_version:
                    stmt_update = """
                    UPDATE {keyspace} SET data=%(data)s, updated_at=NOW() WHERE id = %(id)s;
                    """.format(keyspace=keyspace)
                    await cursor.execute(stmt_update, {
                        'id': str(stream),
                        'data': eventstream.decode(),
                    })
