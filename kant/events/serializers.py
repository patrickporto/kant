from json import JSONEncoder, JSONDecoder
from .models import EventModel


class EventModelEncoder(JSONEncoder):
    """
    A class serializer for EventModel to be converted to json
    >>> found_added = FoundAdded(amount=25.5)
    >>> isinstance(found_added, EventModel)
    True
    >>> json.dumps(found_added, cls=EventModelEncoder)
    '{"$version": 0, "amount": 25.5, "$type": "FoundAdded"}'
    """
    def default(self, obj):
        if isinstance(obj, EventModel):
            return obj.decode()
        return JSONEncoder.default(self, obj)
