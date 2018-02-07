class VersionError(Exception):
    pass


class StreamExists(VersionError):
    def __init__(self, event, *args, **kwargs):
        message = "The EventStream is not empty. The Event '{}' cannot be added.".format(event.__class__.__name__)
        super().__init__(message, *args, **kwargs)


class DependencyDoesNotExist(VersionError):
    def __init__(self, event, dependencies, *args, **kwargs):
        message = "The Event '{}' expected {}.".format(
            event.__class__.__name__,
            dependencies,
        )
        super().__init__(message, *args, **kwargs)


class DatabaseError(Exception):
    pass


class IntegrityError(DatabaseError):
    pass


class StreamDoesNotExist(DatabaseError):
    pass
