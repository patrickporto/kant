from operator import attrgetter
from copy import deepcopy
import json
from kant.events.models import EventModel
from kant.events.serializers import EventModelEncoder


class EventStream:
    def __init__(self, events=[]):
        self.initial_version = -1
        self.current_version = -1
        self._events = set()
        for event in events:
            self.initial_version += 1
            self.add(event)

    def __eq__(self, event_stream):
        return self.current_version == event_stream.current_version

    def __len__(self):
        return len(self._events)

    def __add__(self, event_stream):
        events = self._events + event_stream.events
        events.sort(key=attrgetter('version'))
        return EventStream(events, events[-1].version)

    def __iter__(self):
        return iter(sorted(self._events, key=attrgetter('version')))

    def __repr__(self):
        return str(list(self))

    def add(self, event):
        if event not in self._events:
            self.current_version += 1
            event.version = self.current_version
            self._events.add(event)

    def decode(self):
        return json.dumps(list(self._events), cls=EventModelEncoder)

    @classmethod
    def loads(self, obj):
        return EventStream([EventModel.loads(event) for event in obj])
