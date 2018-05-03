from operator import attrgetter

import sqlalchemy as sa
from async_generator import async_generator, yield_
from kant import aggregates, events, projections
from kant.eventstore import EventStream
from kant.projections import ProjectionError, ProjectionRouter
from kant.projections.sa import SQLAlchemyProjectionAdapter
from sqlalchemy.schema import CreateTable, DropTable

import pytest


class BankAccountCreated(events.Event):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.Event):
    amount = events.DecimalField()


class WithdrawalPerformed(events.Event):
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
async def statement(saconnection):
    statement = sa.Table('statement', sa.MetaData(),  # NOQA
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('owner', sa.String(255)),
        sa.Column('balance', sa.Integer),
    )
    await saconnection.execute(CreateTable(statement))
    await yield_(statement)
    await saconnection.execute(DropTable(statement))


@pytest.mark.asyncio
async def test_projection_should_create_projection(saconnection, eventsourcing, statement):
    # arrange
    class Statement(projections.Projection):
        id = projections.IntegerField()
        owner = projections.CharField()
        balance = projections.IntegerField()

        def when_bank_account_created(self, event):
            self.id = event.id
            self.owner = event.owner
            self.balance = 0

    # act
    router = ProjectionRouter()
    router.add('event_store', statement, Statement)
    projection_adapter = SQLAlchemyProjectionAdapter(saconnection, router)
    eventsourcing.projections.bind(projection_adapter)

    bank_account = BankAccount()
    bank_account.dispatch(BankAccountCreated(
        id=123,
        owner='John Doe',
    ))
    async with eventsourcing.open('event_store') as eventstore:
        await eventstore.append_to_stream(bank_account.id, bank_account.get_events())
    # assert
    result = await saconnection.execute(statement.select())
    result = list(result)
    assert len(result) == 1
    assert result[0].id == 123
    assert result[0].owner == 'John Doe'
    assert result[0].balance == 0


@pytest.mark.asyncio
async def test_projection_should_update_projection(saconnection, eventsourcing, statement):
    # arrange
    class Statement(projections.Projection):
        __keyspace__ = 'event_store'
        id = projections.IntegerField(primary_key=True)
        owner = projections.CharField()
        balance = projections.IntegerField()

        def when_bank_account_created(self, event):
            self.id = event.id
            self.owner = event.owner
            self.balance = 0

        def when_deposit_performed(self, event):
            self.balance += event.amount

    # act
    router = ProjectionRouter()
    router.add('event_store', statement, Statement)
    projection_adapter = SQLAlchemyProjectionAdapter(saconnection, router)
    eventsourcing.projections.bind(projection_adapter)

    bank_account_1 = BankAccount()
    bank_account_1.dispatch(BankAccountCreated(
        id=321,
        owner='John Doe',
    ))
    bank_account_2 = BankAccount()
    bank_account_2.dispatch(BankAccountCreated(
        id=789,
        owner='John Doe',
    ))
    async with eventsourcing.open('event_store') as eventstore:
        await eventstore.append_to_stream(bank_account_1.id, bank_account_1.get_events(), bank_account_1.notify_save)
        await eventstore.append_to_stream(bank_account_2.id, bank_account_2.get_events(), bank_account_2.notify_save)
        bank_account_1.dispatch(DepositPerformed(
            amount=20,
        ))
        bank_account_1.dispatch(DepositPerformed(
            amount=20,
        ))
        await eventstore.append_to_stream(bank_account_1.id, bank_account_1.get_events(), bank_account_1.notify_save)

    # assert
    result = await saconnection.execute(statement.select())
    result = sorted(list(result), key=attrgetter('id'))
    assert len(result) == 2
    assert result[0].id == 321
    assert result[0].owner == 'John Doe'
    assert result[0].balance == 40
    assert result[1].id == 789
    assert result[1].owner == 'John Doe'
    assert result[1].balance == 0


@pytest.mark.asyncio
async def test_projection_should_raise_exception_when_update_without_primary_keys(saconnection, eventsourcing, statement):
    # arrange
    class Statement(projections.Projection):
        __keyspace__ = 'event_store'
        id = projections.IntegerField()
        owner = projections.CharField()
        balance = projections.IntegerField()

        def when_bank_account_created(self, event):
            self.id = event.id
            self.owner = event.owner
            self.balance = 0

        def when_deposit_performed(self, event):
            self.balance += event.amount

    # act
    router = ProjectionRouter()
    router.add('event_store', statement, Statement)
    projection_adapter = SQLAlchemyProjectionAdapter(saconnection, router)
    eventsourcing.projections.bind(projection_adapter)

    bank_account = BankAccount()
    bank_account.dispatch(BankAccountCreated(
        id=456,
        owner='John Doe',
    ))
    async with eventsourcing.open('event_store') as eventstore:
        await eventstore.append_to_stream(bank_account.id, bank_account.get_events(), bank_account.notify_save)
        bank_account.dispatch(DepositPerformed(
            amount=20,
        ))
        bank_account.dispatch(DepositPerformed(
            amount=20,
        ))
        # assert
        with pytest.raises(ProjectionError):
            await eventstore.append_to_stream(bank_account.id, bank_account.get_events(), bank_account.notify_save)
