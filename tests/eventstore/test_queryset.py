from kant.eventstore import QuerySet


def test_queryset_should_get_by_id():
    aggregate_id = 123
    # act
    query = QuerySet().filter(id=123)
    # assert
    assert query() == ('SELECT * FROM event_store WHERE id = %(id)s', {'id': 123})


def test_queryset_should_get_by_id_and_data():
    aggregate_id = 123
    # act
    query = QuerySet().filter(id=123, data=None)
    # assert
    assert query() == ('SELECT * FROM event_store WHERE id = %(id)s AND data = %(data)s', {'id': 123, 'data': None})
