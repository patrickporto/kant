from kant.events import DecimalField, Event
from kant.exceptions import EventDoesNotExist

import pytest


def test_event_should_encode_obj():
    # arrange
    class MyEvent(Event):
        amount = DecimalField()

    serialized = {"$type": "MyEvent", "amount": 20}
    # act
    my_event_model = Event.make(serialized)
    # assert
    assert isinstance(my_event_model, MyEvent), type(my_event_model)
    assert my_event_model.amount == 20


def test_event_should_raise_when_encode_invalid_obj():
    # arrange
    serialized = {"$type": "UtopicEvent", "$version": 0, "amount": 20}
    # act and assert
    with pytest.raises(EventDoesNotExist):
        my_event_model = Event.make(serialized)
