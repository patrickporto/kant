from .datamapper.exceptions import *  # NOQA
from .events.exceptions import *  # NOQA
from .eventstore.exceptions import *  # NOQA


class CommandError(Exception):
    pass
