from copy import deepcopy
from async_generator import yield_, async_generator
from inflection import underscore
from kant.datamapper.base import ModelMeta, FieldMapping
from kant.datamapper.fields import *  # NOQA
from kant.eventstore import EventStream, get_connection
from .exceptions import AggregateError


class Manager:
    def __init__(self, model, keyspace, using=None):
        self._model = model
        self._conn = using or get_connection()
        self.keyspace = keyspace

    async def save(self, aggregate_id, events, notify_save):
        async with self._conn.open(self.keyspace) as eventstore:
            await eventstore.append_to_stream(aggregate_id, events, notify_save)

    async def get(self, aggregate_id):
        async with self._conn.open(self.keyspace) as eventstore:
            stream = await eventstore.get_stream(aggregate_id)
            return self._model.from_stream(stream)

    @async_generator
    async def all(self):
        async with self._conn.open(self.keyspace) as eventstore:
            async for stream in eventstore.all_streams():
                await yield_(self._model.from_stream(stream))

    async def get_stream(self, aggregate_id):
        async with self._conn.open(self.keyspace) as eventstore:
            return await eventstore.get_stream(aggregate_id)


class AggregateMeta(ModelMeta):
    def __new__(mcs, class_name, bases, attrs):
        cls = ModelMeta.__new__(mcs, class_name, bases, attrs)
        if '__keyspace__' in attrs.keys():
            cls.objects = Manager(model=cls, keyspace=attrs['__keyspace__'])
        return cls


class Aggregate(FieldMapping, metaclass=AggregateMeta):
    def __init__(self):
        super().__init__()
        self._all_events = EventStream()
        self._events = EventStream()
        self._stored_events = EventStream()

    def all_events(self):
        return self._all_events

    def stored_events(self):
        return self._stored_events

    def get_events(self):
        return self._events

    def notify_save(self, new_version):
        self._events.clear()
        self._events.initial_version = new_version
        self._all_events.initial_version = new_version
        self._stored_events.initial_version = new_version

    def fetch_events(self, events: EventStream):
        self._stored_events = deepcopy(events)
        self._all_events = deepcopy(self._stored_events)
        self._events.initial_version = events.initial_version
        for event in events:
            self.dispatch(event, flush=False)

    def apply(self, event):
        event_name = underscore(event.__class__.__name__)
        method_name = 'apply_{0}'.format(event_name)
        try:
            method = getattr(self, method_name)
            method(event)
        except AggregateError:
            msg = "The command for '{}' is not defined".format(event.__class__.__name__)
            raise CommandError(msg)

    def dispatch(self, events, flush=True):
        if isinstance(events, list):
            received_events = list(events)
        else:
            received_events = [events]
        for event in received_events:
            self.apply(event)
            if flush:
                self._events.add(event)
                self._all_events.add(event)

    @property
    def current_version(self):
        return self._all_events.current_version

    @property
    def version(self):
        return self._all_events.initial_version

    @classmethod
    def from_stream(cls, stream):
        self = cls()
        self.fetch_events(stream)
        return self

    async def save(self):
        return await self.objects.save(self.get_pk(), self.get_events(), self.notify_save)

    async def refresh_from_db(self):
        stream = await self.objects.get_stream(self.get_pk())
        self.fetch_events(stream)
        return self
