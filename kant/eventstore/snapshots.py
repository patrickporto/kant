from .stream import EventStream


class Snapshot:
    def __init__(self, data, version):
        self.data = data
        self.version = version
    
    def eventstream(self):
        pass
