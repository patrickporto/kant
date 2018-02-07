import pytest
from kant.eventstore.stream import EventStream
from kant.eventstore.exceptions import StreamExists, DependencyDoesNotExist
from kant import events


class BankAccountCreated(events.Event):
    __empty_stream__ = True

    id = events.CUIDField(primary_key=True)
    owner = events.CharField()


class DepositPerformed(events.Event):
    amount = events.DecimalField()


class WithdrawalPerformed(events.Event):
    amount = events.DecimalField()


class OwnerChanged(events.Event):
    __dependencies__ = ['BankAccountCreated']

    new_owner = events.CharField()


@pytest.mark.asyncio
async def test_eventstream_should_append_new_event():
    # arrange
    bank_account_created = BankAccountCreated(
        id='052c21b6-aab9-4311-b954-518cd04f704c',
        owner='John Doe'
    )
    # act
    event_stream = EventStream()
    event_stream.add(bank_account_created)
    # assert
    assert len(event_stream) == 1
    assert event_stream.current_version == 0
    assert list(event_stream)[0] == bank_account_created


@pytest.mark.asyncio
async def test_eventstream_should_append_new_event_only_once():
    # arrange
    bank_account_created = BankAccountCreated(
        id='052c21b6-aab9-4311-b954-518cd04f704c',
        owner='John Doe'
    )
    # act
    event_stream = EventStream()
    event_stream.add(bank_account_created)
    event_stream.add(bank_account_created)
    # assert
    assert len(event_stream) == 1
    assert event_stream.current_version == 0
    assert list(event_stream)[0] == bank_account_created


@pytest.mark.asyncio
async def test_eventstream_should_raise_stream_exists_when_stream_exists():
    # arrange
    bank_account_created_1 = BankAccountCreated(
        id='052c21b6-aab9-4311-b954-518cd04f704c',
        owner='John Doe'
    )
    bank_account_created_2 = BankAccountCreated(
        id='052c21b6-aab9-4311-b954-518cd04f704c',
        owner='John Doe'
    )
    # act
    event_stream = EventStream()
    event_stream.add(bank_account_created_1)
    # assert
    with pytest.raises(StreamExists):
        event_stream.add(bank_account_created_2)


@pytest.mark.asyncio
async def test_eventstream_should_raise_version_error_when_dependency_not_found():
    # arrange
    owner_changed = OwnerChanged(
        new_owner='Jane Doe',
    )
    # act and assert
    with pytest.raises(DependencyDoesNotExist) as e:
        event_stream = EventStream()
        event_stream.add(owner_changed)
