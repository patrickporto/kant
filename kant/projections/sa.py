from sqlalchemy import and_, literal_column
from .exceptions import ProjectionError, ProjectionDoesNotExist


class SQLAlchemyProjectionAdapter:
    def __init__(self, saconnection, router):
        self.saconnection = saconnection
        self.router = router

    async def handle_create(self, keyspace, steam, eventstream):
        projection = self.router.get_projection(keyspace, eventstream)
        stmt = self.router.get_model(keyspace).insert().values(**projection.decode())
        await self.saconnection.execute(stmt)

    async def handle_update(self, keyspace, steam, eventstream):
        projection = self.router.get_projection(keyspace, eventstream)
        if not projection.primary_keys():
            msg = "'{}' not have primary keys".format(projection.__class__.__name__)
            raise ProjectionError(msg)
        stmt = self.router.get_model(keyspace).update().values(
            **projection.decode()
        ).where(
            and_(
                literal_column(field) == value for field, value in projection.primary_keys().items()
            )
        )
        await self.saconnection.execute(stmt)
