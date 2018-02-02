from copy import deepcopy
from inflection import underscore
from functools import wraps


class Projection:
    pass


class connect_projection:
    def __init__(self, saconnection, table):
        self.table = table
        self.saconnection = saconnection

    def __call__(self, projection):
        self.projection = projection
        self.projection.__aggregate__.subscribe(self.when)
        self.projection.table = self.table
        self.projection.saconnection = self.saconnection
        return self.projection

    def when(self, aggregate, event):
        event_name = underscore(event.__class__.__name__)
        method_name = 'when_{0}'.format(event_name)
        method = getattr(self.projection, method_name)
        prev_state = deepcopy(aggregate)
        next_state = method(prev_state, event)
        self.save(prev_state, next_state)

    def save(self, prev_state, next_state):
        data = {key: value for key, value in prev_state.serializeditems()}
        if prev_state.primary_keys():
            stmt = self._table.update().values(**data)
        else:
            stmt = self._table.insert().values(**data)
        self._saconnection.execute(stmt)
