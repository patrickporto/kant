from kant.eventstore.schema import create_table, drop_table


def test_create_table_should_create_table_if_not_exists(dbsession):
    # act
    create_table(dbsession)
    # assert
    with dbsession.cursor() as cursor:
        cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'event_store'
        );
        """)
        (exists,) = cursor.fetchone()
        assert exists


def test_drop_table_should_drop_table_if_exists(dbsession):
    # arrange
    create_table(dbsession)
    # act
    drop_table(dbsession)
    # assert
    with dbsession.cursor() as cursor:
        cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'event_store'
        );
        """)
        (exists,) = cursor.fetchone()
        assert not exists
