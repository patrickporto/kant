from kant.events.models import EventModel


class QuerySet:
    def __init__(self):
        self._where = []

    def __call__(self):
        operation = 'SELECT * FROM event_store'
        parameters = {}
        stmt_parameters = []

        for (name, value, lookup,) in self._where:
            parameters[name] = value
            stmt_param = '{0} {1} %({0})s'.format(name, lookup)
            if isinstance(value, EventModel):
                parameters[name] = value.decode()
                stmt_param = '{0} {1} %({0})s::jsonb'.format(name, lookup)
            stmt_parameters.append(stmt_param)

        if len(stmt_parameters) > 0:
            operation += ' WHERE ' + ' AND '.join(stmt_parameters)
        return (operation, parameters)

    def filter(self, *args, **kwargs):
        for name, value in kwargs.items():
            operator = '='
            if isinstance(value, EventModel):
                operator = '@>'
            self._where.append((name, value, operator))
        return self
