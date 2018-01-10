from kant.db.backends import Field
from kant.db.backends.postgresql import DatabaseWrapper


def test_create_table_should_return_sql_create_table():
    # arrange
    table_name = 'event_store'
    columns = [
        Field(
            name='id',
            type='uuid',
            primary_key=True,
            null=False,
        ),
        Field(
            name='data',
            type='json',
            primary_key=False,
            null=True,
        ),
        Field(
            name='created_at',
            type='timestamp',
            primary_key=False,
            null=False,
        ),
    ]
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.create_table(name=table_name, columns=columns)
    # assert
    expected_sql = (
        'CREATE TABLE event_store '
        '(id uuid,data json,created_at timestamp NOT NULL,PRIMARY KEY (id))'
    )

    assert sql == expected_sql.strip()


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


def test_drop_index_should_return_sql_drop_index():
    # arrange
    name = 'event_store_id'
    database_wrapper = DatabaseWrapper()
    # act
    sql = database_wrapper.drop_index(
        name=name,
    )
    # assert
    assert sql == 'DROP INDEX event_store_id'
