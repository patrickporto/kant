from copy import deepcopy
from inflection import underscore
from kant.eventstore.stream import EventStream
from kant.datamapper.base import ModelMeta, FieldMapping
from kant.datamapper.fields import *  # NOQA


class ProjectionManager:
    def __init__(self):
        self._adapters = set()

    def bind(self, adapter):
        self._adapters.add(adapter)

    async def notify_create(self, *args, **kwargs):
        for adapter in self._adapters:
            await adapter.handle_create(*args, **kwargs)

    async def notify_update(self, *args, **kwargs):
        for adapter in self._adapters:
            await adapter.handle_update(*args, **kwargs)


class Projection(FieldMapping, metaclass=ModelMeta):
    def fetch_events(self, eventstream):
        for event in eventstream:
            self.when(event)

    def when(self, event):
        event_name = underscore(event.__class__.__name__)
        method_name = 'when_{0}'.format(event_name)
        try:
            method = getattr(self, method_name)
            method(event)
        except AttributeError:
            pass


class ProjectionRouter:
    def __init__(self):
        self._projections = {}
        self._models = {}

    def add(self, keyspace, model, projection):
        self._models[keyspace] = model
        self._projections[keyspace] = projection

    def get_projection(self, keyspace, eventstream):
        if keyspace not in self._projections:
            raise ProjectionDoesNotExist(keyspace)
        Projection = self._projections[keyspace]
        projection = Projection()
        projection.fetch_events(eventstream)
        return projection

    def get_model(self, keyspace):
        if keyspace not in self._models:
            raise ProjectionDoesNotExist(keyspace)
        return self._models[keyspace]
