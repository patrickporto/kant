from collections.abc import MutableMapping
from kant.eventstore import EventStoreConnection, EventStream
from kant.eventstore.schema import create_table


def test_event_store_connection_should_have_streams(dbsession):
    # arrange
    create_table(dbsession)
    # act
    connection = EventStoreConnection(dbsession)
    # assert
    assert connection.streams is not None
    assert isinstance(connection.streams, MutableMapping)


def test_streams_should_get_stream(dbsession):
    # arrange
    create_table(dbsession)
    # act
    connection = EventStoreConnection(dbsession)
    stream = connection.streams.get('test-stream')
    # assert
    assert isinstance(stream, EventStream)
