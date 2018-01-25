from abc import ABCMeta
from pprint import pformat
from collections import MutableMapping
from kant.events.fields import Field


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
