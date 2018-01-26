from copy import deepcopy
import json
import pytest
from fixtures import BankAccountCreated, DepositPerformed, WithdrawalPerformed
from kant.aggregates import Aggregate
from kant.exceptions import ObjectDoesNotExist, VersionError
from kant.eventstore.repositories import EventStoreRepository
from kant.eventstore.schema import create_table
from kant.eventstore.stream import EventStream


@pytest.mark.asyncio
async def test_save_should_create_event_store(dbsession):
    # arrange
    await create_table(dbsession)
    aggregate_id = '052c21b6-aab9-4311-b954-518cd04f704c'
    events = EventStream([
        BankAccountCreated(
            id=aggregate_id,
            owner='John Doe'
        )
    ])
    # act
    async with dbsession.cursor() as cursor:
        event_store_repository = EventStoreRepository(cursor)
        last_version = await event_store_repository.save(
            aggregate_id=aggregate_id,
            events=events,
        )
        # assert
        stmt = """
        SELECT event_store.id, event_store.data, event_store.created_at
        FROM event_store WHERE event_store.id = %(id)s
        """
        await cursor.execute(stmt, {'id': aggregate_id})
        event_store_list = await cursor.fetchall()
        assert last_version == 0
        assert cursor.rowcount == 1
        # id
        assert event_store_list[0][0] == aggregate_id
        # events
        assert len(event_store_list[0][1]) == 1
        # first event
        assert event_store_list[0][1][0]['$type'] == 'BankAccountCreated'
        assert event_store_list[0][1][0]['$version'] == 0
        assert event_store_list[0][1][0]['id'] == aggregate_id
        assert event_store_list[0][1][0]['owner'] == 'John Doe'
        # date created
        assert event_store_list[0][2] is not None


@pytest.mark.asyncio
async def test_get_should_return_events(dbsession):
    # arrange
    await create_table(dbsession)
    stmt = """
    INSERT INTO event_store (id, data, created_at, updated_at)
    VALUES (%(id)s, %(data)s, NOW(), NOW())
    """
    aggregate_id = 'e0fbeecc-d68f-45b1-83c7-5cbc65f78af7'
    async with dbsession.cursor() as cursor:
        await cursor.execute(stmt, {
            'id': aggregate_id,
            'data': json.dumps([{
                '$type': 'BankAccountCreated',
                '$version': 0,
                'id': aggregate_id,
                'owner': 'John Doe',
            }]),
        })
        # act
        event_store_repository = EventStoreRepository(cursor)
        stored_events = await event_store_repository.get(aggregate_id)
        # assert
        stored_events = list(stored_events)
        assert len(stored_events) == 1
        assert isinstance(stored_events[0], BankAccountCreated)
        assert stored_events[0].version == 0
        assert stored_events[0].id == aggregate_id
        assert stored_events[0].owner == 'John Doe'


@pytest.mark.asyncio
async def test_get_should_raise_exception_when_not_found(dbsession):
    # arrange
    await create_table(dbsession)
    aggregate_id = 'f2283f9d-9ed2-4385-a614-53805725cbac',
    async with dbsession.cursor() as cursor:
        event_store_repository = EventStoreRepository(cursor)
        # act and assert
        with pytest.raises(ObjectDoesNotExist):
            await event_store_repository.get(
                aggregate_id=aggregate_id,
            )


@pytest.mark.asyncio
async def test_save_should_raise_version_error_when_diff(dbsession):
    # arrange
    await create_table(dbsession)
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
    async with dbsession.cursor() as cursor:
        event_store_repository = EventStoreRepository(cursor)
        await event_store_repository.save(
            aggregate_id=aggregate_id,
            events=events_base,
        )
        # act
        stored_events = await event_store_repository.get(
            aggregate_id=aggregate_id,
        )
        stored_events_1 = deepcopy(stored_events)
        stored_events_2 = deepcopy(stored_events)
        stored_events_1 += events_1
        stored_events_2 += events_2
        await event_store_repository.save(
            aggregate_id=aggregate_id,
            events=stored_events_1,
        )
        # assert
        with pytest.raises(VersionError):
            await event_store_repository.save(
                aggregate_id=aggregate_id,
                events=stored_events_2,
            )
