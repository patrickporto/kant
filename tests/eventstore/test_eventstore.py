from copy import deepcopy
from os import environ
import json
import pytest
from kant.aggregates import Aggregate
from kant.exceptions import ObjectDoesNotExist, VersionError
from kant.eventstore.connection import connect
from kant.eventstore.stream import EventStream
from kant import events


class BankAccountCreated(events.EventModel):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.EventModel):
    amount = events.DecimalField()


class WithdrawalPerformed(events.EventModel):
    amount = events.DecimalField()


class MyObjectCreated(events.EventModel):
    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


@pytest.fixture
async def connection(dbsession):
    eventstore = await connect(
        pool=dbsession,
    )
    await eventstore.create_keyspace('event_store')
    return eventstore


@pytest.mark.asyncio
async def test_save_should_create_event_store(dbsession, connection):
    # arrange
    aggregate_id = '052c21b6-aab9-4311-b954-518cd04f704c'
    events = EventStream([
        BankAccountCreated(
            id=aggregate_id,
            owner='John Doe'
        )
    ])
    # act
    async with connection.open('event_store/{}'.format(aggregate_id), 'w') as eventstream:
        eventstream += events
    # assert
    async with dbsession.cursor() as cursor:
        stmt = """
        SELECT event_store.id, event_store.data, event_store.created_at
        FROM event_store WHERE event_store.id = %(id)s
        """
        result = await cursor.execute(stmt, {'id': aggregate_id})
        event_store = await cursor.fetchone()
        assert event_store is not None
        assert cursor.rowcount == 1
        # id
        assert event_store[0] == aggregate_id
        assert event_store[1][0]['$type'] == 'BankAccountCreated'
        assert event_store[1][0]['$version'] == 0
        assert event_store[1][0]['id'] == aggregate_id
        assert event_store[1][0]['owner'] == 'John Doe'
        assert event_store[2] is not None


@pytest.mark.asyncio
async def test_get_should_return_events(dbsession, connection):
    # arrange
    stmt = """
    INSERT INTO event_store (id, data, created_at, updated_at)
    VALUES (%(id)s, %(data)s, NOW(), NOW())
    """
    aggregate_id = 'e0fbeecc-d68f-45b1-83c7-5cbc65f78af7'
    # act
    async with dbsession.cursor() as cursor:
        await cursor.execute(stmt, {
            'id': aggregate_id,
            'data': json.dumps([{
                '$type': 'MyObjectCreated',
                '$version': 0,
                'id': aggregate_id,
                'owner': 'John Doe',
            }]),
        })
    # act
    async with connection.open('event_store/{}'.format(aggregate_id), 'r') as eventstream:
        stored_events = list(eventstream)
    # assert
    assert len(stored_events) == 1
    assert isinstance(stored_events[0], MyObjectCreated)
    assert stored_events[0].version == 0
    assert stored_events[0].id == aggregate_id
    assert stored_events[0].owner == 'John Doe'


@pytest.mark.asyncio
async def test_get_should_raise_exception_when_not_found(dbsession, connection):
    # arrange
    aggregate_id = 'f2283f9d-9ed2-4385-a614-53805725cbac',
    # act and assert
    with pytest.raises(ObjectDoesNotExist):
        async with connection.open('event_store/{}'.format(aggregate_id), 'r') as eventstream:
            pass


@pytest.mark.asyncio
async def test_save_should_raise_version_error_when_optimistic(dbsession, connection):
    # arrange
    aggregate_id = 'f2283f9d-9ed2-4385-a614-53805725cbac',
    events_base = EventStream([
        BankAccountCreated(
            id=aggregate_id,
            owner='John Doe'
        )
    ])
    events_1 = EventStream([
        DepositPerformed(
            amount=20
        )
    ])
    events_2 = EventStream([
        WithdrawalPerformed(
            amount=20
        )
    ])
    async with connection.open('event_store/{}'.format(aggregate_id), 'w') as eventstream:
        eventstream += events_base
    # act and assert
    ctx_1 = connection.open('event_store/{}'.format(aggregate_id), 'r', optimistic=True)
    ctx_2 = connection.open('event_store/{}'.format(aggregate_id), 'r', optimistic=True)
    with pytest.raises(VersionError):
        async with ctx_1 as eventstream_1, ctx_2 as eventstream_2:
            eventstream_1 += events_1
            eventstream_2 += events_2
