from .backends.aiopg import EventStoreConnection


async def connect(dsn=None, user=None, password=None, host=None, database=None, *, pool=None):
    settings = {
        'dsn': dsn,
        'user': user,
        'password': password,
        'host': host,
        'database': database,
        'pool': pool,
    }
    return await EventStoreConnection.create(settings)
