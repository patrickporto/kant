from abc import ABCMeta
from kant.exceptions import EventDoesNotExist
from kant.events.base import ModelMeta, FieldMapping
from kant.events.fields import *  # NOQA


class EventModel(FieldMapping, metaclass=ModelMeta):
    EVENTMODEL_JSON_COLUMN = '$type'

    version = IntegerField(default=0, json_column='$version')

    @classmethod
    def loads(self, obj):
        event_name = obj[self.EVENTMODEL_JSON_COLUMN]
        events = [Event for Event in self.__subclasses__() if Event.__name__ == event_name]
        try:
            Event = events[0]
        except IndexError:
            raise EventDoesNotExist()
        del obj[self.EVENTMODEL_JSON_COLUMN]
        json_columns = {}
        for name, field in Event.concrete_fields.items():
            json_column = field.json_column or name
            json_columns[json_column] = name
        args = {json_columns[name]: value for name, value in obj.items()}
        return Event(**args)

    def decode(self):
        event = {key: value for key, value in self.serializeditems()}
        event.update({
            self.EVENTMODEL_JSON_COLUMN: self.__class__.__name__,
        })
        return event


class SchemaModel(FieldMapping, metaclass=ModelMeta):

    @classmethod
    def from_dict(self, obj, cls):
        Event = cls
        json_columns = {}
        for name, field in Event.concrete_fields.items():
            json_column = field.json_column or name
            json_columns[json_column] = name
        args = {json_columns[name]: value for name, value in obj.items()}
        return Event(**args)

    def decode(self):
        event = {key: value for key, value in self.serializeditems()}
        return event
