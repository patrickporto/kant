from operator import attrgetter
import json
from kant.events import Event
from .exceptions import StreamExists, DependencyDoesNotExist


class EventStream:
    def __init__(self, events=None):
        self.initial_version = -1
        self.current_version = -1
        self._events = set()
        if events is not None:
            for event in list(events):
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

    def _valid_empty_stream(self, event):
        if event.__empty_stream__ and len(self._events) > 0:
            raise StreamExists(event)

    def _valid_dependencies(self, event):
        event_names = [event.__class__.__name__ for event in self._events]
        not_found = [event for event in event.__dependencies__ if event not in event_names]
        if len(not_found) > 0:
            raise DependencyDoesNotExist(event, not_found)

    def _conflict_resolution(self, event):
        self._valid_empty_stream(event)
        self._valid_dependencies(event)
        return event

    def exists(self):
        return self.initial_version != -1

    def clear(self):
        self._events = set()

    def add(self, event):
        if event not in self._events:
            event = self._conflict_resolution(event)
            self.current_version += 1
            event.version = self.current_version
            self._events.add(event)

    def decode(self):
        return [event.decode() for event in self._events]

    def json(self):
        return json.dumps(self.decode(), sort_keys=True)

    @classmethod
    def make(self, obj):
        return EventStream([Event.make(event) for event in obj])
