from unittest.mock import patch, Mock
import pytest
from kant.eventstore import Query
from kant.eventstore.schema import create_table
from tests.fixtures import BankAccountCreated


@pytest.mark.asyncio
async def test_queryset_should_filter_by_id(dbsession):
    # arrange
    aggregate_id = 123

    async def execute(*args, **kwargs):
        async def fetchall(*args, **kwargs):
            return []
        mock = Mock()
        mock.fetchall.side_effect = fetchall
        return mock

    async with dbsession.cursor() as cursor:
        await create_table(cursor)
        # act
        with patch.object(cursor, 'execute', side_effect=execute) as mock_execute:
            query = Query(cursor).filter(id=aggregate_id)
            [r async for r in query]
        # assert
        expected_operation = 'SELECT * FROM event_store WHERE id = %(id)s'
        expected_parameters = {'id': aggregate_id}
        mock_execute.assert_called_once_with(expected_operation, expected_parameters)


@pytest.mark.asyncio
async def test_queryset_should_filter_by_id_and_data(dbsession):
    # arrange
    aggregate_id = 123

    async def execute(*args, **kwargs):
        async def fetchall(*args, **kwargs):
            return []
        mock = Mock()
        mock.fetchall.side_effect = fetchall
        return mock

    async with dbsession.cursor() as cursor:
        await create_table(cursor)
        # act
        with patch.object(cursor, 'execute', side_effect=execute) as mock_execute:
            query = Query(cursor).filter(id=aggregate_id, data=None)
            [r async for r in query]
        # assert
        expected_operation = 'SELECT * FROM event_store WHERE id = %(id)s AND data = %(data)s'
        expected_parameters = {'id': aggregate_id, 'data': None}
        mock_execute.assert_called_once_with(expected_operation, expected_parameters)


@pytest.mark.asyncio
async def test_queryset_should_filter_by_id_list(dbsession):
    # arrange
    aggregate1_id = 123
    aggregate2_id = 456

    async def execute(*args, **kwargs):
        async def fetchall(*args, **kwargs):
            return []
        mock = Mock()
        mock.fetchall.side_effect = fetchall
        return mock

    async with dbsession.cursor() as cursor:
        await create_table(cursor)
        # act
        with patch.object(cursor, 'execute', side_effect=execute) as mock_execute:
            query = Query(cursor).filter(id=[aggregate1_id, aggregate2_id])
            [r async for r in query]
        # assert
        expected_operation = 'SELECT * FROM event_store WHERE id IN (%(id)s)'
        expected_parameters = {'id': [aggregate1_id, aggregate2_id]}
        mock_execute.assert_called_once_with(expected_operation, expected_parameters)


@pytest.mark.asyncio
async def test_queryset_should_filter_by_event(dbsession):
    # arrange
    aggregate_id = '123'
    bank_account_created = BankAccountCreated(
        id='123',
        owner='John Doe',
    )

    async def execute(*args, **kwargs):
        async def fetchall(*args, **kwargs):
            return []
        mock = Mock()
        mock.fetchall.side_effect = fetchall
        return mock

    async with dbsession.cursor() as cursor:
        await create_table(cursor)
        # act
        with patch.object(cursor, 'execute', side_effect=execute) as mock_execute:
            query = Query(cursor).filter(id=aggregate_id, data=bank_account_created)
            [r async for r in query]
        # assert
        expected_operation = 'SELECT * FROM event_store WHERE id = %(id)s AND data @> %(data)s::jsonb'
        expected_param_event = {
            "$type": "BankAccountCreated",
            "$version": 0,
            "id": "123",
            "owner": "John Doe"
        }
        expected_parameters = {'id': aggregate_id, 'data': expected_param_event}
        mock_execute.assert_called_once_with(expected_operation, expected_parameters)
