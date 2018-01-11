from difflib import ndiff


class ConsistencyError(Exception):
    def __init__(self, message, ours, theirs, *args, **kwargs):
        super().__init__(self, message, *args, **kwargs)
        self.ours = ours
        self.theirs = theirs
        self.diff_events = ndiff(ours, theirs)


class ObjectDoesNotExist(Exception):
    pass
