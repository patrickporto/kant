from collections.abc import MutableMapping
import pytest
from kant.eventstore import EventStoreConnection, EventStream
from kant.eventstore.schema import create_table


@pytest.mark.asyncio
async def test_event_store_connection_should_have_streams(dbsession):
    # arrange
    await create_table(dbsession)
    # act
    connection = EventStoreConnection(dbsession)
    # assert
    assert connection.streams is not None
    assert isinstance(connection.streams, MutableMapping)


@pytest.mark.asyncio
async def test_streams_should_get_stream(dbsession):
    # arrange
    await create_table(dbsession)
    # act
    connection = EventStoreConnection(dbsession)
    stream = await connection.streams.get('test-stream')
    # assert
    assert isinstance(stream, EventStream)