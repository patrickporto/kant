class StreamManager(object):
    def __init__(self, session):
        self._session = session


class EventStoreConnection(object):
    def __init__(self, session):
        self._session = session
        self.streams = StreamManager(session)
