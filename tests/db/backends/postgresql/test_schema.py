from kant.db.backends.postgresql import DatabaseWrapper


def test_create_table_should_return_sql_create_table():
    # arrange
    table_name = 'event_store'
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.create_table(name=table_name)
    # assert
    assert sql == 'CREATE TABLE event_store'


def test_drop_table_should_return_sql_drop_table():
    # arrange
    table_name = 'event_store'
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.drop_table(name=table_name)
    # assert
    assert sql == 'DROP TABLE event_store'


def test_create_index_should_return_sql_create_index():
    # arrange
    name = 'event_store_id'
    table = 'event_store'
    column = 'id'
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.create_index(
        name=name,
        table=table,
        columns=[column],
    )
    # assert
    assert sql == 'CREATE INDEX event_store_id ON event_store (id)'
