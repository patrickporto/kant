from operator import attrgetter
import json
from kant.events.models import EventModel
from kant.events.serializers import EventModelEncoder


class EventStream:
    def __init__(self, events, version=0):
        self._events = events
        self.version = version

    def __eq__(self, event_stream):
        return event_stream.version == event_stream.version

    def __len__(self):
        return len(self._events)

    def __getitem__(self, key):
        return self._events[key]

    def __add__(self, event_stream):
        events = self._events + event_stream.events
        events.sort(key=attrgetter('version'))
        return EventStream(events, events[-1].version)

    def __iter__(self):
        return iter(sorted(self._events, key=attrgetter('version')))

    def __repr__(self):
        return sorted(self._events, key=attrgetter('version'))

    def append(self, event):
        self._events.append(event)

    def dumps(self):
        return json.dumps(self._events, cls=EventModelEncoder)

    @classmethod
    def loads(self, obj):
        return EventStream([EventModel.loads(event) for event in obj])
