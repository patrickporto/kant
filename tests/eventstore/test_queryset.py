from kant.eventstore import QuerySet
from tests.fixtures import BankAccountCreated


def test_queryset_should_filter_by_id():
    # arrange
    aggregate_id = 123
    # act
    query = QuerySet().filter(id=aggregate_id)
    # assert
    assert query() == ('SELECT * FROM event_store WHERE id = %(id)s', {'id': aggregate_id})


def test_queryset_should_filter_by_id_and_data():
    # arrange
    aggregate_id = 123
    # act
    query = QuerySet().filter(id=aggregate_id, data=None)
    # assert
    expected_operation = 'SELECT * FROM event_store WHERE id = %(id)s AND data = %(data)s'
    expected_parameters = {'id': aggregate_id, 'data': None}
    assert query() == (expected_operation, expected_parameters)


def test_queryset_should_filter_by_id_list():
    # arrange
    aggregate1_id = 123
    aggregate2_id = 456
    # act
    query = QuerySet().filter(id=[aggregate1_id, aggregate2_id])
    # assert
    expected_operation = 'SELECT * FROM event_store WHERE id IN (%(id)s)'
    expected_parameters = {'id': [aggregate1_id, aggregate2_id]}
    assert query() == (expected_operation, expected_parameters)


def test_queryset_should_filter_by_event():
    # arrange
    aggregate_id = '123'
    bank_account_created = BankAccountCreated(
        id='123',
        owner='John Doe',
    )
    # act
    query = QuerySet().filter(id=aggregate_id, data=bank_account_created)
    # assert
    expected_operation = 'SELECT * FROM event_store WHERE id = %(id)s AND data @> %(data)s::jsonb'
    expected_param_event = {
        "$type": "BankAccountCreated",
        "$version": 0,
        "id": "123",
        "owner": "John Doe"
    }
    expected_parameters = {'id': aggregate_id, 'data': expected_param_event}
    assert query() == (expected_operation, expected_parameters)
