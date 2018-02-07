from datetime import datetime
import json
import pytest
from kant import events


class FoundAdded(events.Event):
    amount = events.DecimalField()


class AccountSchemaModel(events.SchemaModel):
    balance = events.DecimalField()


@pytest.fixture(autouse=True)
def event_model_example(doctest_namespace):
    doctest_namespace['FoundAdded'] = FoundAdded
    doctest_namespace['json'] = json
    doctest_namespace['datetime'] = datetime
    doctest_namespace['AccountSchemaModel'] = AccountSchemaModel
