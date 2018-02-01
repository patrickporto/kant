import pytest
from kant.events import EventModel, DecimalField
from kant.exceptions import EventDoesNotExist


def test_eventmodel_should_encode_obj():
    # arrange
    class MyEventModel(EventModel):
        amount = DecimalField()

    serialized = {
        '$type': 'MyEventModel',
        'amount': 20,
    }
    # act
    my_event_model = EventModel.make(serialized)
    # assert
    assert isinstance(my_event_model, MyEventModel), type(my_event_model)
    assert my_event_model.amount == 20


def test_eventmodel_should_raise_when_encode_invalid_obj():
    # arrange
    serialized = {
        '$type': 'UtopicEvent',
        'amount': 20,
    }
    # act and assert
    with pytest.raises(EventDoesNotExist):
        my_event_model = EventModel.make(serialized)
