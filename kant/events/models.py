from json import JSONDecoder, JSONEncoder
from datetime import datetime
from decimal import Decimal
from abc import ABCMeta
from uuid import uuid1, UUID
from pprint import pformat
from collections import MutableMapping
import json
from dateutil import parser as dateutil_parser


class Field(metaclass=ABCMeta):
    def __init__(self, default=None, json_column=None, *args, **kwargs):
        self.default = default
        self.json_column = json_column

    def encode(self, value):
        return value

    def parse(self, value):
        return value

    def default_value(self):
        if callable(self.default):
            return self.default()
        return self.default


class UUIDField(Field):
    def __init__(self, primary_key=False, *args, **kwargs):
        self.primary_key = primary_key
        super().__init__(*args, **kwargs)
        if self.primary_key:
            self.default = lambda: uuid1()

    def encode(self, value):
        return str(value)

    def parse(self, value):
        if isinstance(value, UUID):
            return value
        return UUID(value)


class DecimalField(Field):
    def encode(self, value):
        return float(value)

    def parse(self, value):
        return Decimal(value)


class IntegerField(Field):
    def encode(self, value):
        return int(value)

    def parse(self, value):
        return int(value)


class DateTimeField(Field):
    def __init__(self, auto_now=False, *args, **kwargs):
        self.auto_now = auto_now
        super().__init__(*args, **kwargs)
        if self.auto_now:
            self.default = lambda: datetime.now()

    def encode(self, value):
        """
        >>> field = DateTimeField()
        >>> create_at = datetime(2009, 5, 28, 16, 15)
        >>> field.encode(create_at)
        '2009-05-28T16:15:00'
        """
        return value.isoformat()

    def parse(self, value):
        """
        >>> field = DateTimeField()
        >>> field.parse('2009-05-28T16:15:00')
        datetime.datetime(2009, 5, 28, 16, 15)
        >>> create_at = datetime(2009, 5, 28, 16, 15)
        >>> field.parse(create_at)
        datetime.datetime(2009, 5, 28, 16, 15)
        """
        if isinstance(value, str):
            return dateutil_parser.parse(value)
        if not isinstance(value, datetime):
            raise TypeError('expected string or datetime object')
        return value


class CharField(Field):
    def encode(self, value):
        """
        >>> field = CharField()
        >>> field.encode(123)
        '123'
        """
        return str(value)

    def parse(self, value):
        """
        >>> field = CharField()
        >>> field.parse(123)
        '123'
        """
        return str(value)


class BooleanField(Field):
    def encode(self, value):
        """
        >>> field = BooleanField()
        >>> field.encode(True)
        'true'
        >>> field.encode(False)
        'false'
        """
        if value:
            return 'true'
        return 'false'

    def parse(self, value):
        """
        >>> field = BooleanField()
        >>> field.parse(True)
        True
        >>> field.parse(False)
        False
        >>> field.parse('true')
        True
        >>> field.parse('false')
        False
        """
        if isinstance(value, str) and value.strip() == 'false':
            return False
        return bool(value)


class SchemaField(Field):
    def __init__(self, to, *args, **kwargs):
        self.to = to
        super().__init__(*args, **kwargs)

    def encode(self, value):
        """
        >>> account = AccountSchemaModel(balance=25.5)
        >>> field = SchemaField(to=AccountSchemaModel)
        >>> field.encode(account)
        {'balance': 25.5}
        """
        return value.decode()

    def parse(self, value):
        """
        >>> account = AccountSchemaModel(balance=25.5)
        >>> field = SchemaField(to=AccountSchemaModel)
        >>> field.parse(account)
        <AccountSchemaModel {'balance': Decimal('25.5')}>
        >>> field.parse({"balance": 30 })
        <AccountSchemaModel {'balance': Decimal('30')}>
        """
        if isinstance(value, self.to):
            return value
        return self.to().from_dict(value, cls=self.to)


class EventModelMeta(ABCMeta):
    def __new__(mcs, class_name, bases, attrs):
        if not hasattr(mcs, '_sub_cls'):
            mcs._sub_cls = {}
        concrete_fields = {}
        new_attrs = {}
        for name, value in attrs.items():
            if isinstance(value, Field):
                concrete_fields[name] = value
            else:
                new_attrs[name] = value

        cls = type.__new__(mcs, class_name, bases, new_attrs)
        cls.concrete_fields = cls.concrete_fields.copy()
        cls.concrete_fields.update(concrete_fields)
        if class_name not in ['EventModel', 'SchemaModel']:
            mcs._sub_cls[class_name] = cls
        return cls


class EventFieldMapping(MutableMapping):
    concrete_fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        initial = {name: value.default_value() for name, value in self.concrete_fields.items() if value.default is not None}
        initial.update(dict(*args, **kwargs))
        if args or kwargs:  # avoid creating dict for most common case
            for name, value in initial.items():
                self[name] = value

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self.concrete_fields:
            try:
                self._values[key] = self.concrete_fields[key].parse(value)
            except TypeError as e:
                msg = ("The value '{value}' is invalid. "
                       "The field '{key}' {exception}").format(
                    value=repr(value),
                    field=key,
                    exception=str(e),
                )
                raise TypeError(msg)
        else:
            msg = '{class_name} does not support field: {field}'.format(
                class_name=self.__class__.__name__,
                field=key,
            )
            raise KeyError(msg)

    def __delitem__(self, key):
        del self._values[key]

    def __getattr__(self, name):
        if name not in self.concrete_fields:
            raise AttributeError(name)
        return self._values[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        self._values[name] = self.concrete_fields[name].parse(value)

    def keys(self):
        return self._values.keys()

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, pformat(dict(self)))

    def copy(self):
        return self.__class__(self)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def serializeditems(self):
        for name, value in self._values.items():
            field_name = self.concrete_fields[name].json_column or name
            field_value = self.concrete_fields[name].encode(value)
            yield (field_name, field_value)


class EventModel(EventFieldMapping, metaclass=EventModelMeta):
    EVENTMODEL_JSON_COLUMN = '$type'

    version = IntegerField(default=0, json_column='$version')

    __metaclass__ = EventModelMeta

    def event_name(self):
        return self.__class__.__name__

    @classmethod
    def from_dict(self, obj):
        event_name = obj[self.EVENTMODEL_JSON_COLUMN]
        cls = self._sub_cls[event_name]
        del obj[self.EVENTMODEL_JSON_COLUMN]
        json_columns = {}
        for name, field in cls.concrete_fields.items():
            json_column = field.json_column or name
            json_columns[json_column] = name
        args = {json_columns[name]: value for name, value in obj.items()}
        return cls(**args)

    def decode(self):
        event = {key: value for key, value in self.serializeditems()}
        event.update({
            self.EVENTMODEL_JSON_COLUMN: self.event_name(),
        })
        return event


class SchemaModel(EventFieldMapping, metaclass=EventModelMeta):

    @classmethod
    def from_dict(self, obj, cls):
        json_columns = {}
        for name, field in cls.concrete_fields.items():
            json_column = field.json_column or name
            json_columns[json_column] = name
        args = {json_columns[name]: value for name, value in obj.items()}
        return cls(**args)

    def decode(self):
        event = {key: value for key, value in self.serializeditems()}
        return event
