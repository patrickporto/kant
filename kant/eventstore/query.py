from kant.events.models import EventModel


class Query:
    def __init__(self, cursor):
        self.cursor = cursor
        self._where = []
        self._parameters = {}

    async def __aiter__(self):
        operation = 'SELECT * FROM event_store'
        operation += self._stmt_parameters()
        result = await self.cursor.execute(operation, self._parameters)
        result = await result.fetchall()
        for row in result:
            yield row

    def _stmt_parameters(self):
        stmt = ''
        stmt_parameters = []
        for (name, value, lookup,) in self._where:
            if isinstance(value, EventModel):
                stmt_param = self._clean_event(name, value, lookup)
            elif isinstance(value, list):
                stmt_param = self._clean_list(name, value, lookup)
            else:
                stmt_param = self._clean_default(name, value, lookup)
            stmt_parameters.append(stmt_param)

        if len(stmt_parameters) > 0:
            stmt = ' WHERE ' + ' AND '.join(stmt_parameters)
        return stmt

    def _clean_event(self, name, value, lookup):
        self._parameters[name] = value.decode()
        stmt_param = '{0} {1} %({0})s::jsonb'.format(name, lookup)
        return stmt_param

    def _clean_list(self, name, value, lookup):
        self._parameters[name] = value
        stmt_param = '{0} {1} (%({0})s)'.format(name, lookup)
        return stmt_param

    def _clean_default(self, name, value, lookup):
        self._parameters[name] = value
        stmt_param = '{0} {1} %({0})s'.format(name, lookup)
        return stmt_param

    def filter(self, *args, **kwargs):
        for name, value in kwargs.items():
            operator = '='
            if isinstance(value, EventModel):
                operator = '@>'
            elif isinstance(value, list):
                operator = 'IN'
            self._where.append((name, value, operator))
        return self
