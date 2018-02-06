from copy import deepcopy
from inflection import underscore
from kant.eventstore.stream import EventStream
from kant.datamapper.base import ModelMeta, FieldMapping
from kant.datamapper.fields import *  # NOQA


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
