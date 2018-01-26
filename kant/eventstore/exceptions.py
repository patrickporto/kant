class VersionError(Exception):
    def __init__(self, current_version, expected_version, ours, theirs, *args, **kwargs):
        message = "The version is {current_version}, but the expected is {expected_version}".format(
            current_version=current_version,
            expected_version=expected_version,
        )
        super().__init__(self, message, *args, **kwargs)


class ObjectDoesNotExist(Exception):
    pass
