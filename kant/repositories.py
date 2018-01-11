from operator import attrgetter
from datetime import datetime
import json

from sqlalchemy_utils import UUIDType
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa
from .exceptions import ConsistencyError, ObjectDoesNotExist
from kant.events.serializers import EventModelEncoder
from kant.events.models import EventModel


class EventStoreRepository:
    def __init__(self, session, event_store_name):
        self.session = session
        self.EventStore = sa.Table(event_store_name, sa.MetaData(),  # NOQA
            sa.Column('id', UUIDType(binary=False), primary_key=True),
            sa.Column('version', sa.Integer),
            sa.Column('data', JSONB),
            sa.Column('metadata', JSONB),
            sa.Column('created', sa.DateTime, default=datetime.now()),
        )

    async def save(self, entity_id, events, expected_version):
        """ Save the events in the model """
        try:
            stored_events = await self.get(entity_id=entity_id)
            stored_events = sorted(stored_events, key=attrgetter('version'))

            if stored_events[-1]['version'] != expected_version:
                raise ConsistencyError(
                    message="The version is {current_version}, but the expected is {expected_version}".format(
                        current_version=events[-1]['version'],
                        expected_version=expected_version,
                    ),
                    ours=events,
                    theirs=stored_events,
                )
            events[:0] = stored_events

            stmt = self.EventStore.update().where(
                self.EventStore.c.id == entity_id,
            )
        except ObjectDoesNotExist:
            stmt = self.EventStore.insert().values(
                id=entity_id,
            )
        new_version = events[-1]['version']
        await self.session.execute(stmt.values(
            version=new_version,
            data=[json.dumps(event, cls=EventModelEncoder) for event in events],
        ))
        return new_version

    async def get(self, *, entity_id, initial_version=0):
        results = await self.session.execute(
            self.EventStore.select().where(
                sa.and_(
                    self.EventStore.c.id == entity_id,
                    self.EventStore.c.data.op('?')('version').cast(sa.Integer) >= initial_version,
                )
            )
        )
        event_store = await results.fetchone()
        if not event_store:
            raise ObjectDoesNotExist()
        return sorted([EventModel.from_dict(json.loads(event)) for event in event_store.data], key=attrgetter('version'))

    def event_store(self):
        return self.EventStore


class EventRepository():
    def __init__(self, session):
        self.session = session
        self.event_store_repository = EventStoreRepository(session, self.event_store_name)

    def event_store(self):
        return self.event_store_repository.event_store()
