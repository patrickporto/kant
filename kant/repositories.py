from operator import attrgetter
from datetime import datetime
import json

from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa
from .exceptions import ConsistencyError, ObjectDoesNotExist
from kant.events.serializers import EventModelEncoder
from kant.events import EventModel, EventStream


class EventStoreRepository:
    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.EventStore = sa.Table('event_store', sa.MetaData(),  # NOQA
            sa.Column('id', sa.String),
            sa.Column('version', sa.Integer),
            sa.Column('data', JSONB),
            sa.Column('metadata', JSONB),
            sa.Column('created', sa.DateTime, default=datetime.now()),
        )

    async def save(self, entity_id, events, expected_version=0):
        """ Save the events in the model """
        transaction = await self.session.begin()
        events = events if isinstance(events, EventStream) else EventStream(events)
        try:
            stored_events = await self.get(entity_id=entity_id)
            if stored_events.version != expected_version:
                raise ConsistencyError(
                    current_version=events[-1]['version'],
                    expected_version=expected_version,
                    ours=events,
                    theirs=stored_events,
                )
            entity_events = stored_events + events
            stmt = """
            UPDATE event_store SET data=%(data)s, updated_at=NOW() WHERE id = %(id)s;
            """
        except ObjectDoesNotExist:
            entity_events = events
            stmt = """
            INSERT INTO event_store (id, data, created_at, updated_at)
            VALUES (%(id)s, %(data)s, NOW(), NOW())
            """
        await self.session.execute(stmt, {
            'id': str(entity_id),
            'data': entity_events.dumps()
        })
        return entity_events.version

    async def get(self, entity_id, initial_version=0):
        stmt = """
        SELECT event_store.id, event_store.data, event_store.created_at
        FROM event_store WHERE event_store.id = %(id)s AND CAST(data ? '$version' AS INTEGER) >= %(version)s
        """
        await self.session.execute(stmt, {
            'id': str(entity_id),
            'version': initial_version,
        })
        event_store = await self.session.fetchone()
        if not event_store:
            raise ObjectDoesNotExist()
        return EventStream([EventModel.loads(event) for event in event_store[1]])

    def event_store(self):
        return self.EventStore


class EventRepository():
    def __init__(self, session):
        self.session = session
        self.event_store_repository = EventStoreRepository(session, self.event_store_name)

    def event_store(self):
        return self.event_store_repository.event_store()
