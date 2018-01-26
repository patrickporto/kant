from operator import attrgetter
from datetime import datetime
import json

from kant.exceptions import VersionError, ObjectDoesNotExist, StreamExists
from kant.events.serializers import EventModelEncoder
from kant.events import EventModel
from kant.eventstore.stream import EventStream


class EventStoreRepository:
    def __init__(self, session, *args, **kwargs):
        self.session = session

    async def update(self, aggregate_id, events: EventStream):
        async with self.session.begin() as transaction:
            stmt_select = """
            SELECT event_store.data
            FROM event_store WHERE event_store.id = %(id)s AND CAST(data ? '$version' AS INTEGER) >= %(version)s
            FOR UPDATE
            """
            await self.session.execute(stmt_select, {
                'id': str(aggregate_id),
                'version': events.initial_version,
            })
            event_store = await self.session.fetchone()
            if not event_store:
                raise ObjectDoesNotExist()
            stored_events = EventStream.make(event_store[0])
            if stored_events > events:
                message = "The version is {current_version}, but the expected is {expected_version}".format(
                    current_version=stored_events.initial_version,
                    expected_version=events.initial_version,
                )
                raise VersionError(message)
            stored_events += events
            stmt_update = """
            UPDATE event_store SET data=%(data)s, updated_at=NOW() WHERE id = %(id)s;
            """
            await self.session.execute(stmt_update, {
                'id': str(aggregate_id),
                'data': stored_events.decode(),
            })

    async def create(self, aggregate_id, events: EventStream):
        stmt = """
        INSERT INTO event_store (id, data, created_at, updated_at)
        VALUES (%(id)s, %(data)s, NOW(), NOW())
        """
        await self.session.execute(stmt, {
            'id': str(aggregate_id),
            'data': events.decode(),
        })

    async def save(self, aggregate_id, events: EventStream):
        """ Save the events in the model """
        try:
            await self.update(aggregate_id, events)
        except ObjectDoesNotExist:
            await self.create(aggregate_id, events)
        return events.current_version

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
        return EventStream.make(event_store[0])
