import json
import pytest
from fixtures import BankAccountCreated
from kant import TrackedEntity
from kant.exceptions import ObjectDoesNotExist
from kant.repositories import EventStoreRepository
from kant.eventstore.schema import create_table


class BankAccount(TrackedEntity):
    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.get('owner')


@pytest.mark.asyncio
async def test_save_should_create_event_store(dbsession):
    # arrange
    await create_table(dbsession)
    bank_account_created = BankAccountCreated(
        owner='John Doe'
    )
    # act
    async with dbsession.cursor() as cursor:
        event_store_repository = EventStoreRepository(cursor)
        bank_account = BankAccount()
        bank_account.dispatch(bank_account_created)
        last_version = await event_store_repository.save(
            entity_id=bank_account.id,
            events=bank_account.get_events(),
            expected_version=bank_account.version,
        )
        # assert
        stmt = """
        SELECT event_store.id, event_store.data, event_store.created_at
        FROM event_store WHERE event_store.id = %(id)s
        """
        await cursor.execute(stmt, {'id': bank_account.id})
        event_store_list = await cursor.fetchall()
        assert last_version == 0
        assert cursor.rowcount == 1
        # id
        assert event_store_list[0][0] == bank_account_created.id
        # events
        assert len(event_store_list[0][1]) == 1
        # first event
        assert event_store_list[0][1][0]['$type'] == 'BankAccountCreated'
        assert event_store_list[0][1][0]['$version'] == 0
        assert event_store_list[0][1][0]['id'] == bank_account_created.id
        assert event_store_list[0][1][0]['owner'] == bank_account_created.owner
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
    entity_id = 'e0fbeecc-d68f-45b1-83c7-5cbc65f78af7'
    async with dbsession.cursor() as cursor:
        await cursor.execute(stmt, {
            'id': entity_id,
            'data': json.dumps([{
                '$type': 'BankAccountCreated',
                '$version': 0,
                'id': entity_id,
                'owner': 'Joe Doe',
            }]),
        })
        # act
        event_store_repository = EventStoreRepository(cursor)
        stored_events = await event_store_repository.get(entity_id)
        # assert
        assert len(stored_events) == 1
        assert isinstance(stored_events[0], BankAccountCreated)
        assert stored_events[0].version == 0
        assert stored_events[0].id == entity_id
        assert stored_events[0].owner == 'Joe Doe'


@pytest.mark.asyncio
async def test_get_should_raise_exception_when_not_found(dbsession):
    # arrange
    await create_table(dbsession)
    entity_id = 'e0fbeecc-d68f-45b1-83c7-5cbc65f78af7',
    async with dbsession.cursor() as cursor:
        event_store_repository = EventStoreRepository(cursor)
        # act and assert
        with pytest.raises(ObjectDoesNotExist):
            await event_store_repository.get(
                entity_id=entity_id,
            )
