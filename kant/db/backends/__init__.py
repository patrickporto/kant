from collections import namedtuple


Field = namedtuple('Field', [
    'name',
    'type',
    'primary_key',
    'null',
])
