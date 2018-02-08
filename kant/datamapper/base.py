from abc import ABCMeta
from collections import MutableMapping
import json
from .fields import Field
from .exceptions import FieldError


class ModelMeta(ABCMeta):
    def __new__(mcs, class_name, bases, attrs):
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
        return cls


class FieldMapping(MutableMapping):
    concrete_fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        initial = {}
        for name, value in self.concrete_fields.items():
            if value.default is not None:
                initial[name] = value.default_value()
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
            return super().__getattribute__(name)
        return self._values[name]

    def __setattr__(self, name, value):
        if name not in self.concrete_fields:
            return super().__setattr__(name, value)
        try:
            if value is not None:
                self._values[name] = self.concrete_fields[name].parse(value)
        except KeyError:
            msg = "The field '{0}' is not defined in '{1}'.".format(name, self.__class__.__name__)
            raise FieldError(msg)

    def keys(self):
        return self._values.keys()

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self._values)

    def copy(self):
        return self.__class__(self)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __hash__(self):
        return id(self)

    def serializeditems(self):
        for name, value in self._values.items():
            field_name = self.concrete_fields[name].json_column or name
            field_value = self.concrete_fields[name].encode(value)
            yield (field_name, field_value)

    def decode(self):
        return {key: value for key, value in self.serializeditems()}

    def json(self, only=None):
        data = self.decode()
        if only is not None:
            data = {key: value for key, value in data.items() if key in only}
        return json.dumps(data, sort_keys=True)

    def primary_keys(self):
        primary_keys = {}
        for name, value in self._values.items():
            field = self.concrete_fields[name]
            field_name = field.json_column or name
            field_value = field.encode(value)
            if field.primary_key:
                primary_keys[field_name] = field_value
        return primary_keys

    def get_pk(self):
        primary_keys = list(self.primary_keys().values())
        if not primary_keys:
            msg = "Nothing primary key defined for '{}'".format(self.__class__.__name__)
            raise AggregateError(msg)
        elif len(primary_keys) > 1:
            msg = "Many primary keys defined for '{}'".format(self.__class__.__name__)
            raise AggregateError(msg)
        return primary_keys[0]
