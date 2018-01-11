from unittest.mock import Mock
import pytest


@pytest.fixture
def dbsession():
    rows = []
    mock = Mock()
    cursor = mock.connection.cursor.return_value
    cursor.execute.return_value = rows
    return mock
