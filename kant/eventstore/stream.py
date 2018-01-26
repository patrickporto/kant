from operator import attrgetter
import json
from kant.events.models import EventModel
from kant.events.serializers import EventModelEncoder
from kant.eventstore.exceptions import StreamExists


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

    def __lt__(self, event_stream):
        return self.current_version < event_stream.current_version

    def __le__(self, event_stream):
        return self.current_version <= event_stream.current_version

    def __ne__(self, event_stream):
        return self.current_version != event_stream.current_version

    def __gt__(self, event_stream):
        return self.current_version > event_stream.current_version

    def __ge__(self, event_stream):
        return self.current_version >= event_stream.current_version

    def __len__(self):
        return len(self._events)

    def __add__(self, event_stream):
        for event in event_stream:
            self.add(event)
        return self

    def __iter__(self):
        return iter(sorted(self._events, key=attrgetter('version')))

    def __repr__(self):
        return str(list(self))

    def _conflict_resolution(self, event):
        if event.__empty_stream__ and len(self._events) > 0:
            msg = "The EventStream is not empty. The Event '{}' cannot be added.".format(event.__class__.__name__)
            raise StreamExists(msg)
        return event

    def add(self, event):
        if event not in self._events:
            event = self._conflict_resolution(event)
            self.current_version += 1
            event.version = self.current_version
            self._events.add(event)

    def decode(self):
        return json.dumps(list(self._events), cls=EventModelEncoder)

    @classmethod
    def make(self, obj):
        return EventStream([EventModel.make(event) for event in obj])
