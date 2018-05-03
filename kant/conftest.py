import json
from datetime import datetime

import pytest


@pytest.fixture(autouse=True)
def event_model_example(doctest_namespace):
    doctest_namespace["json"] = json
    doctest_namespace["datetime"] = datetime
