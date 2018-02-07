from async_generator import yield_, async_generator
import pytest
from kant import aggregates, events
from kant.eventstore import connect, EventStream


class BankAccountCreated(events.Event):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.Event):
    amount = events.DecimalField()


class BankAccount(aggregates.Aggregate):
    id = aggregates.IntegerField()
    owner = aggregates.CharField()
    balance = aggregates.IntegerField()

    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.owner
        self.balance = 0

    def apply_deposit_performed(self, event):
        self.balance += event.amount


@pytest.fixture
@async_generator
async def connection(dbsession):
    eventstore = await connect(
        pool=dbsession,
    )
    await eventstore.create_keyspace('event_store')
    await yield_(eventstore)
    await eventstore.drop_keyspace('event_store')

@pytest.mark.asyncio
async def test_eventstore_should_create_snapshot(dbsession, connection):
    # arrange
    events = EventStream([
        BankAccountCreated(
            id=123,
            owner='John Doe',
            version=0,
        )
    ])
    deposit_performed = DepositPerformed(
        amount=20,
    )
    # act
    async with connection.open('event_store') as eventstore:
        bank_account = BankAccount()
        bank_account.fetch_events(events)
        await bank_account.create_snapshot(eventstore)

    # assert
    async with dbsession.cursor() as cursor:
        select_snapshots = """
        SELECT 1 FROM {keyspace}_snapshots WHERE data=%(data)s AND version=%(version)s AND id = %(id)s;
        """
        await cursor.execute(select_snapshots, {
            'keyspace': 'event_store',
            'data': bank_account.json(),
            'id': bank_account.id,
        })
        (exists,) = await cursor.fetchone()
        assert exists


@pytest.mark.asyncio
async def test_eventstore_should_get_snapshot(dbsession, connection):
    # arrange
    events = EventStream([
        BankAccountCreated(
            id=123,
            owner='John Doe',
            version=0,
        )
    ])
    deposit_performed = DepositPerformed(
        amount=20,
    )
    async with connection.open('event_store') as eventstore:
        bank_account = BankAccount()
        bank_account.fetch_events(events)
        await eventstore.append_to_stream(bank_account.id, bank_account.get_events(), bank_account.notify_save)
        await bank_account.create_snapshot(eventstore)
    # act
    async with connection.open('event_store') as eventstore:
        stored_aggregate = BankAccount.from_snapshot(eventstore)
        stored_aggregate.dispatch(deposit_performed)
        await eventstore.append_to_stream(bank_account.id, bank_account.get_events(), bank_account.notify_save)
        stored_aggregate = await eventstore.get_stream(bank_account.id)
    # assert
    assert stored_aggregate.version == 1
    assert stored_aggregate.id == bank_account.id
    assert stored_aggregate.owner == 'Tim Clock'
    assert stored_aggregate.version == 1
    assert stored_aggregate.amount == 20
