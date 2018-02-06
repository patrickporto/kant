from .exceptions import ProjectionError


class SQLAlchemyProjectionAdapter:
    def __init__(self, saconnection):
        self.saconnection = saconnection
        self._projections = {}
        self._tables = {}

    def register(self, table, projection):
        self._tables[projection.__keyspace__] = table
        self._projections[projection.__keyspace__] = projection

    def _get_projection(self, keyspace, eventstream):
        if keyspace not in self._projections:
            raise ProjectionError("Projection for '{}' not found".format(keyspace))
        Projection = self._projections[keyspace]
        projection = Projection()
        projection.fetch_events(eventstream)
        return projection

    async def handle_create(self, keyspace, steam, eventstream):
        projection = self._get_projection(keyspace, eventstream)
        stmt = self._tables[keyspace].insert().values(**projection.decode())
        await self.saconnection.execute(stmt)

    async def handle_update(self, keyspace, steam, eventstream):
        projection = self._get_projection(keyspace, eventstream)
        stmt = self._tables[keyspace].update().values(**projection.decode())
        await self.saconnection.execute(stmt)
