from difflib import ndiff


class ConsistencyError(Exception):
    def __init__(self, current_version, expected_version, ours, theirs, *args, **kwargs):
        message = "The version is {current_version}, but the expected is {expected_version}".format(
            current_version=current_version,
            expected_version=expected_version,
        )
        super().__init__(self, message, *args, **kwargs)
        self.ours = ours
        self.theirs = theirs
        self.diff_events = ndiff(ours, theirs)


class ObjectDoesNotExist(Exception):
    pass


class EventDoesNotExist(Exception):
    pass
