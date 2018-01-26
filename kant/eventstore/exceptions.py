class VersionError(Exception):
    pass


class StreamExists(VersionError):
    pass


class ObjectDoesNotExist(Exception):
    pass
