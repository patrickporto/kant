from copy import deepcopy
from operator import attrgetter
from os import environ
import json
import pytest
from kant.aggregates import Aggregate
from kant.exceptions import StreamDoesNotExist, VersionError
from kant.eventstore.stream import EventStream
from kant import events


class BankAccountCreated(events.Event):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.Event):
    amount = events.DecimalField()


class WithdrawalPerformed(events.Event):
    amount = events.DecimalField()


class MyObjectCreated(events.Event):
    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


@pytest.mark.asyncio
async def test_save_should_create_event_store(dbsession, eventsourcing):
    # arrange
    aggregate_id = '052c21b6-aab9-4311-b954-518cd04f704c'
    events = EventStream([
        BankAccountCreated(
            id=aggregate_id,
            owner='John Doe'
        )
    ])
    # act
    async with eventsourcing.open('event_store') as eventstore:
        await eventstore.append_to_stream(aggregate_id, events)
        result = await eventstore.get_stream(aggregate_id)

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
async def test_eventstore_should_fetch_one_stream(dbsession, eventsourcing):
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
    async with eventsourcing.open('event_store') as eventstore:
        stored_events = await eventstore.get_stream(aggregate_id)
    # assert
    assert len(stored_events) == 1
    event = list(stored_events)[0]
    assert isinstance(event, MyObjectCreated)
    assert event.version == 0
    assert event.id == aggregate_id
    assert event.owner == 'John Doe'


@pytest.mark.asyncio
async def test_eventstore_should_fetch_all_streams(dbsession, eventsourcing):
    # arrange
    stmt = """
    INSERT INTO event_store (id, data, created_at, updated_at)
    VALUES (%(id)s, %(data)s, NOW(), NOW())
    """
    aggregate1_id = '1'
    aggregate2_id = '2'
    # act
    async with dbsession.cursor() as cursor:
        await cursor.execute(stmt, {
            'id': aggregate1_id,
            'data': json.dumps([{
                '$type': 'BankAccountCreated',
                '$version': 0,
                'id': aggregate1_id,
                'owner': 'John Doe',
            }]),
        })
        await cursor.execute(stmt, {
            'id': aggregate2_id,
            'data': json.dumps([
                {
                    '$type': 'BankAccountCreated',
                    '$version': 0,
                    'id': aggregate2_id,
                    'owner': 'Tim Clock',
                },
                {
                    '$type': 'DepositPerformed',
                    '$version': 1,
                    'amount': 20,
                },
            ]),
        })
    # act
    async with eventsourcing.open('event_store') as eventstore:
        stored_eventstreams = []
        async for stream in eventstore.all_streams():
            stored_eventstreams.append(stream)
        stored_eventstreams = sorted(stored_eventstreams, key=attrgetter('current_version'))

    # assert
    assert len(stored_eventstreams) == 2
    eventstream_1 = list(stored_eventstreams[0])
    eventstream_2 = list(stored_eventstreams[1])
    assert eventstream_1[0].version == 0
    assert eventstream_1[0].id == aggregate1_id
    assert eventstream_1[0].owner == 'John Doe'
    assert eventstream_2[0].version == 0
    assert eventstream_2[0].id == aggregate2_id
    assert eventstream_2[0].owner == 'Tim Clock'
    assert eventstream_2[1].version == 1
    assert eventstream_2[1].amount == 20


@pytest.mark.asyncio
async def test_get_should_raise_exception_when_not_found(eventsourcing):
    # arrange
    aggregate_id = 'f2283f9d-9ed2-4385-a614-53805725cbac',
    # act and assert
    async with eventsourcing.open('event_store') as eventstore:
        with pytest.raises(StreamDoesNotExist):
            stored_events = await eventstore.get_stream(aggregate_id)


@pytest.mark.asyncio
async def test_eventstore_should_raise_version_error(dbsession, eventsourcing):
    # arrange
    aggregate_id = 'f2283f9d-9ed2-4385-a614-53805725cbac'
    events_base = EventStream([
        BankAccountCreated(
            id=aggregate_id,
            owner='John Doe'
        )
    ])
    events = EventStream([
        DepositPerformed(
            amount=20
        )
    ])
    async with eventsourcing.open('event_store') as eventstore:
        await eventstore.append_to_stream(aggregate_id, events_base)

    # act
    async with dbsession.cursor() as cursor:
        stmt = """
        UPDATE event_store SET version=%(version)s
        WHERE id = %(id)s;
        """
        await cursor.execute(stmt, {
            'id': aggregate_id,
            'version': 10,
        })
    # assert
    with pytest.raises(VersionError):
        async with eventsourcing.open('event_store') as eventstore:
            await eventstore.append_to_stream(aggregate_id, events)
