class QuerySet:
    def __init__(self):
        self._where = []

    def __call__(self):
        operation = 'SELECT * FROM event_store'
        parameters = {}
        stmt_parameters = []

        for (name, value, lookup,) in self._where:
            parameters[name] = value
            stmt_parameters.append('{0} {1} %({0})s'.format(name, lookup))

        if len(stmt_parameters) > 0:
            operation += ' WHERE ' + ' AND '.join(stmt_parameters)
        return (operation, parameters)

    def filter(self, *args, **kwargs):
        for name, value in kwargs.items():
            self._where.append((name, value, '=',))
        return self
