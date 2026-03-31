"""Authentication endpoint tests."""
import pytest


@pytest.mark.asyncio
def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/auth/register",
        json={
            "name": "New Student",
            "email": "newstudent@test.com",
            "password": "Student@123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
def test_register_duplicate_email(client, registered_student):
    """Test registration with duplicate email."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Another Student",
            "email": "student@test.com",
            "password": "Student@123"
        }
    )
    assert response.status_code == 409
    assert response.json()["error"] == "CONFLICT"


@pytest.mark.asyncio
def test_register_missing_fields(client):
    """Test registration with missing fields."""
    response = client.post(
        "/auth/register",
        json={"name": "No Pass Student"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
def test_login_success(client, registered_student):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "Student@123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
def test_login_wrong_password(client, registered_student):
    """Test login with wrong password."""
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
def test_login_nonexistent_email(client):
    """Test login with nonexistent email."""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@test.com", "password": "Password@123"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
def test_get_me_authenticated(client, student_headers):
    """Test get current user info when authenticated."""
    response = client.get("/users/me", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "name" in data


@pytest.mark.asyncio
def test_get_me_unauthenticated(client):
    """Test get current user info without authentication."""
    response = client.get("/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
def test_refresh_token(client, registered_student, db_session):
    """Test token refresh."""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "Student@123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
