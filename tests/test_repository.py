import pytest
from fixtures import BankAccountCreated
from kant import TrackedEntity
from kant.repositories import EventStoreRepository
from kant.eventstore.schema import create_table


class BankAccount(TrackedEntity):
    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.get('owner')


@pytest.mark.asyncio
async def test_event_store_repository_should_save_events(dbsession):
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
        await event_store_repository.save(
            entity_id=bank_account.id,
            events=bank_account.get_events(),
            expected_version=bank_account.version,
        )
    # assert
    stored_bank_account = await event_store_repository.get(id=bank_account.id)
    assert stored_bank_account.version == 0
    assert stored_bank_account.id == bank_account_created.id
    assert stored_bank_account.owner == bank_account_created.owner
