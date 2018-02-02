from sqlalchemy.schema import CreateTable, DropTable
import pytest
import sqlalchemy as sa
from kant.eventstore import EventStream
from kant import aggregates, events
from kant.eventstore.connection import connect
from kant.projections.sa import Projection


metadata = sa.MetaData()


class BankAccountCreated(events.EventModel):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.EventModel):
    amount = events.DecimalField()


class WithdrawalPerformed(events.EventModel):
    amount = events.DecimalField()


class BankAccount(aggregates.Aggregate):
    id = aggregates.IntegerField()
    owner = aggregates.CharField()
    balance = aggregates.IntegerField()

    def apply_bank_account_created(self, event):
        self.id = event.id
        self.owner = event.owner
        self.balance = 0


@pytest.fixture
async def connection(dbsession):
    eventstore = await connect(
        pool=dbsession,
    )
    await eventstore.create_keyspace('event_store')
    return eventstore


@pytest.mark.asyncio
async def test_projection_should_create_projection(saconnection):
    # arrange
    statement = sa.Table('statement', metadata,  # NOQA
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('owner', sa.String(255)),
        sa.Column('balance', sa.Integer),
    )
    await saconnection.execute(DropTable(statement))
    await saconnection.execute(CreateTable(statement))

    class Statement(Projection):
        __aggregate__ = BankAccount

        def when_bank_account_created(self, state, event):
            state.id = event.id
            state.owner = event.owner
            state.balance = 0
            return state

        def when_deposit_performed(self, state, event):
            state.balance += event.amount
            return state

        def when_withdrawal_performed(self, state, event):
            state.balance -= event.amount
            return state

    # act
    bind_projection(statement, saconnection)(Statement)

    bank_account = BankAccount()
    bank_account.dispatch(BankAccountCreated(
        id=123,
        owner='John Doe',
    ))
    # assert
    result = await saconnection.execute(statement.select())
    result = list(result)
    assert len(result) == 1
    assert result[0].id == 123
    assert result[0].owner == 'John Doe'
    assert result[0].balance == 0
