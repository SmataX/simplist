import pytest
from unittest.mock import MagicMock
from src.modules.task_operations import TaskOperations
from src.common.models import Task

@pytest.fixture
def mock_db_storage():
    return MagicMock()

@pytest.fixture
def task_ops(mock_db_storage):
    return TaskOperations(mock_db_storage)

def test_add_task(task_ops, mock_db_storage):
    mock_db_storage.create.return_value = Task(id=1, content="test", user_id=123, completed=False)

    task_data = {"content": "test", "user_id": 123, "completed": False}
    task = task_ops.add(task_data)

    mock_db_storage.create.assert_called_once()
    assert task.content == "test"
    assert task.user_id == 123

def test_get_task(task_ops, mock_db_storage):
    mock_db_storage.get_by_id.return_value = Task(id=1, content="foo", user_id=123, completed=False)

    task = task_ops.get(1)

    mock_db_storage.get_by_id.assert_called_once_with(1, Task)
    assert task.id == 1
    assert task.content == "foo"

def test_get_user_tasks(task_ops, mock_db_storage):
    tasks = [
        Task(id=1, content="a", user_id=123, completed=False),
        Task(id=2, content="b", user_id=123, completed=True),
    ]
    mock_db_storage.get_all_where.return_value = tasks

    result = task_ops.get_user_tasks(123)

    mock_db_storage.get_all_where.assert_called_once()
    assert len(result) == 2
    assert all(t.user_id == 123 for t in result)

def test_delete_task(task_ops, mock_db_storage):
    task_ops.delete(1)
    mock_db_storage.delete.assert_called_once_with(1, Task)

def test_change_status(task_ops, mock_db_storage):
    mock_db_storage.get_by_id.return_value = Task(id=1, content="c", user_id=123, completed=False)
    mock_db_storage.update.return_value = Task(id=1, content="c", user_id=123, completed=True)

    updated = task_ops.change_status(1)

    mock_db_storage.update.assert_called_once_with(1, Task, {"completed": True})
    assert updated.completed is True
