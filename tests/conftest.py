from os import environ
from datetime import datetime
import json
import aiopg
import pytest
from fixtures import AccountSchemaModel, FoundAdded


@pytest.fixture
async def dbsession():
    conn = await aiopg.connect(
        user=environ.get('DATABASE_USER'),
        password=environ.get('DATABASE_PASSWORD'),
        database=environ.get('DATABASE_DATABASE'),
        host=environ.get('DATABASE_HOST', 'localhost'),
        port=environ.get('DATABASE_PORT', 5432),
    )
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def event_model_example(doctest_namespace):
    doctest_namespace['FoundAdded'] = FoundAdded
    doctest_namespace['json'] = json
    doctest_namespace['datetime'] = datetime
    doctest_namespace['AccountSchemaModel'] = AccountSchemaModel
