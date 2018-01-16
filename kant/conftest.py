from datetime import datetime
import json
import pytest
from tests.fixtures import AccountSchemaModel, FoundAdded


@pytest.fixture(autouse=True)
def event_model_example(doctest_namespace):
    doctest_namespace['FoundAdded'] = FoundAdded
    doctest_namespace['json'] = json
    doctest_namespace['datetime'] = datetime
    doctest_namespace['AccountSchemaModel'] = AccountSchemaModel
