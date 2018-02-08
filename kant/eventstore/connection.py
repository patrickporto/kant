from .backends.aiopg import EventStoreConnection


_connection = None


async def connect(dsn=None, user=None, password=None, host=None, database=None, *, pool=None):
    global _connection
    settings = {
        'dsn': dsn,
        'user': user,
        'password': password,
        'host': host,
        'database': database,
        'pool': pool,
    }
    _connection = await EventStoreConnection.create(settings)
    return _connection


def get_connection():
    return _connection
