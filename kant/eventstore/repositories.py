from operator import attrgetter
from datetime import datetime
import json

from kant.exceptions import ConsistencyError, ObjectDoesNotExist
from kant.events.serializers import EventModelEncoder
from kant.events import EventModel
from kant.eventstore.stream import EventStream


class EventStoreRepository:
    def __init__(self, session, *args, **kwargs):
        self.session = session

    async def save(self, aggregate_id, events, expected_version=0):
        """ Save the events in the model """
        async with self.session.begin() as transaction:
            events = events if isinstance(events, EventStream) else EventStream(events)
            try:
                stmt_select = """
                SELECT event_store.data
                FROM event_store WHERE event_store.id = %(id)s AND CAST(data ? '$version' AS INTEGER) >= %(version)s
                FOR UPDATE
                """
                await self.session.execute(stmt_select, {
                    'id': str(aggregate_id),
                    'version': expected_version,
                })
                event_store = await self.session.fetchone()
                if not event_store:
                    raise ObjectDoesNotExist()
                stored_events = EventStream.loads(event_store[0])
                if stored_events.version != expected_version:
                    raise ConsistencyError(
                        current_version=events[-1]['version'],
                        expected_version=expected_version,
                        ours=events,
                        theirs=stored_events,
                    )
                entity_events = stored_events + events
                stmt_save = """
                UPDATE event_store SET data=%(data)s, updated_at=NOW() WHERE id = %(id)s;
                """
            except ObjectDoesNotExist:
                entity_events = events
                stmt_save = """
                INSERT INTO event_store (id, data, created_at, updated_at)
                VALUES (%(id)s, %(data)s, NOW(), NOW())
                """
            await self.session.execute(stmt_save, {
                'id': str(aggregate_id),
                'data': entity_events.dumps()
            })
            return entity_events.version

    async def get(self, aggregate_id, initial_version=0):
        stmt = """
        SELECT event_store.data
        FROM event_store WHERE event_store.id = %(id)s AND CAST(data ? '$version' AS INTEGER) >= %(version)s
        """
        await self.session.execute(stmt, {
            'id': str(aggregate_id),
            'version': initial_version,
        })
        event_store = await self.session.fetchone()
        if not event_store:
            raise ObjectDoesNotExist()
        return EventStream.loads(event_store[0])
