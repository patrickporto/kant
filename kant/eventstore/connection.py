from .stream import StreamManager


class EventStoreConnection(object):
    def __init__(self, session):
        self._session = session
        self.streams = StreamManager(session)
