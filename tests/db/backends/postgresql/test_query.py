from kant.db.backends.postgresql import Query


def test_query_should_return_select_all():
    # arrange
    table_name = 'event_store'
    # act
    query = Query(table_name).select()
    # assert
    expected_query = 'SELECT * FROM event_store'
    assert expected_query == query


def test_query_should_return_select_with_fields():
    # arrange
    table_name = 'event_store'
    columns = [
        'id',
        'data',
        'created_at',
    ]
    # act
    query = Query(table_name).select(columns)
    # assert
    expected_query = 'SELECT id,data,created_at FROM event_store'
    assert expected_query == query


def test_query_should_return_select_with_str_equality():
    # arrange
    table_name = 'event_store'
    where = {
        'id': '1',
    }
    # act
    query = Query(table_name).select().where(**where)
    # assert
    expected_query = 'SELECT * FROM event_store WHERE id = "1"'
    assert expected_query == query


def test_query_should_return_select_with_number_equality():
    # arrange
    table_name = 'event_store'
    where = {
        'id': 1,
    }
    # act
    query = Query(table_name).select().where(**where)
    # assert
    expected_query = 'SELECT * FROM event_store WHERE id = 1'
    assert expected_query == query


def test_query_should_return_select_with_true_equality():
    # arrange
    table_name = 'event_store'
    where = {
        'is_active': True,
    }
    # act
    query = Query(table_name).select().where(**where)
    # assert
    expected_query = 'SELECT * FROM event_store WHERE is_active = true'
    assert expected_query == query


def test_query_should_return_select_with_false_equality():
    # arrange
    table_name = 'event_store'
    where = {
        'is_active': False,
    }
    # act
    query = Query(table_name).select().where(**where)
    # assert
    expected_query = 'SELECT * FROM event_store WHERE is_active = false'
    assert expected_query == query
