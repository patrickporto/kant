from datetime import datetime
from sqlalchemy import Table, Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import UUIDType
from inflection import underscore


class TrackedEntity:
    def __init__(self):
        self._all_events = []
        self._events = []
        self._stored_events = []
        self.id = None
        self.version = -1
        self.current_version = -1

    def all_events(self):
        return self._all_events

    def stored_events(self):
        return self._stored_events

    def get_events(self):
        return self._events

    def clear_events(self):
        self._events = []

    def fetch_events(self, events):
        self._stored_events = events
        self._all_events = events
        for event in events:
            self.version += 1
            self.dispatch(event, flush=False)

    def apply(self, event):
        event_name = underscore(event.event_name())
        method_name = 'apply_{0}'.format(event_name)
        method = getattr(self, method_name)
        method(event)

    def dispatch(self, event, flush=True):
        self.current_version += 1
        event.version = self.current_version
        self.apply(event)
        if flush:
            self._events.append(event)
            self._all_events.append(event)
