import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, Request
from src.modules import auth_operations as auth
from src.common.models import User


class DummyRequest:
    def __init__(self):
        self.session = {}

# --- Fixtures ---

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def fake_request():
    return DummyRequest()


# --- Tests for hash/verify ---

def test_hash_and_verify_password():
    password = "supersecret"
    hashed = auth.hash_password(password)

    assert hashed != password  # should not be the same
    assert auth.verify_password(password, hashed) is True
    assert auth.verify_password("wrong", hashed) is False


# --- Tests for get_current_user ---

def test_get_current_user_no_session(fake_request, mock_db_session):
    fake_request.session.clear()
    user = auth.get_current_user(fake_request, mock_db_session)
    assert user is None


def test_get_current_user_found(fake_request, mock_db_session):
    fake_request.session["user_id"] = 1
    user = User(id=1, username="u", email="e", password="p")
    mock_db_session.get.return_value = user

    result = auth.get_current_user(fake_request, mock_db_session)
    assert result == user
    mock_db_session.get.assert_called_once_with(User, 1)


def test_get_current_user_not_found(fake_request, mock_db_session):
    fake_request.session["user_id"] = 99
    mock_db_session.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(fake_request, mock_db_session)

    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


# --- Tests for login_user ---

class DummyLoginForm:
    def __init__(self, username, password):
        self.username = username
        self.password = password


def test_login_user_success(fake_request, mock_db_session):
    form = DummyLoginForm("user", "pass")
    user = User(id=1, username="user", email="e", password=auth.hash_password("pass"))

    mock_query = MagicMock()
    mock_query.first.return_value = user
    mock_db_session.exec.return_value = mock_query

    result = auth.login_user(fake_request, mock_db_session, form)

    assert result == user
    mock_db_session.exec.assert_called_once()


def test_login_user_invalid(fake_request, mock_db_session):
    form = DummyLoginForm("user", "wrong")
    user = User(id=1, username="user", email="e", password=auth.hash_password("pass"))

    mock_query = MagicMock()
    mock_query.first.return_value = user
    mock_db_session.exec.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        auth.login_user(fake_request, mock_db_session, form)

    assert exc.value.status_code == 400
    assert "Invalid username or password" in exc.value.detail


def test_login_user_not_found(fake_request, mock_db_session):
    form = DummyLoginForm("user", "pass")

    mock_query = MagicMock()
    mock_query.first.return_value = None
    mock_db_session.exec.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        auth.login_user(fake_request, mock_db_session, form)

    assert exc.value.status_code == 400
    assert "Invalid username or password" in exc.value.detail


# --- Tests for register_user ---

class DummyRegisterForm:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


def test_register_user_success(fake_request, mock_db_session):
    form = DummyRegisterForm("newuser", "new@example.com", "pass")

    # first queries return None → no duplicates
    mock_query = MagicMock()
    mock_query.first.side_effect = [None, None]
    mock_db_session.exec.return_value = mock_query

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda u: setattr(u, "id", 1)

    result = auth.register_user(fake_request, mock_db_session, form)

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    assert auth.verify_password("pass", result.password)


def test_register_user_username_taken(fake_request, mock_db_session):
    form = DummyRegisterForm("exists", "new@example.com", "pass")

    mock_query = MagicMock()
    mock_query.first.side_effect = [User(id=1, username="exists", email="e", password="p")]
    mock_db_session.exec.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        auth.register_user(fake_request, mock_db_session, form)

    assert exc.value.status_code == 400
    assert "Username already taken" in exc.value.detail


def test_register_user_email_taken(fake_request, mock_db_session):
    form = DummyRegisterForm("newuser", "exists@example.com", "pass")

    mock_query = MagicMock()
    # username → None, email → already exists
    mock_query.first.side_effect = [None, User(id=1, username="u", email="exists@example.com", password="p")]
    mock_db_session.exec.return_value = mock_query

    with pytest.raises(HTTPException) as exc:
        auth.register_user(fake_request, mock_db_session, form)

    assert exc.value.status_code == 400
    assert "Email already registered" in exc.value.detail
