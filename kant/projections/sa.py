from sqlalchemy import and_, literal_column
from .exceptions import ProjectionError, ProjectionDoesNotExist


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
            raise ProjectionDoesNotExist(keyspace)
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
        if not projection.primary_keys():
            msg = "'{}' not have primary keys".format(projection.__class__.__name__)
            raise ProjectionError(msg)
        stmt = self._tables[keyspace].update().values(
            **projection.decode()
        ).where(
            and_(
                literal_column(field) == value for field, value in projection.primary_keys().items()
            )
        )
        await self.saconnection.execute(stmt)
