import pytest
from kant.connection import EventStoreConnection


@pytest.mark.asyncio
async def test_connect_should_have_streams(dbsession):
    # act
    connection = EventStoreConnection(dbsession)
    # assert
    assert connection.streams is not None
