import pytest
from kant.eventstore.stream import EventStream
from fixtures import BankAccountCreated


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
    # asert
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
    # asert
    assert len(event_stream) == 1
    assert event_stream.current_version == 0
    assert list(event_stream)[0] == bank_account_created
