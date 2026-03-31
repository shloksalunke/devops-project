"""Rating endpoint tests."""
import pytest


@pytest.mark.asyncio
def test_submit_rating_success(client, student_headers, seed_driver):
    """Test successful rating submission."""
    response = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 5, "comment": "Great driver!"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great driver!"


@pytest.mark.asyncio
def test_submit_duplicate_rating(client, student_headers, seed_driver, db_session):
    """Test duplicate rating submission."""
    # Submit first rating
    response1 = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 5, "comment": "Great!"}
    )
    assert response1.status_code == 201

    # Try to submit again
    response2 = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 4, "comment": "Not as great"}
    )
    assert response2.status_code == 409
    assert response2.json()["error"] == "CONFLICT"


@pytest.mark.asyncio
def test_submit_rating_invalid_low(client, student_headers, seed_driver):
    """Test rating submission with rating too low."""
    response = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 0}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
def test_submit_rating_invalid_high(client, student_headers, seed_driver):
    """Test rating submission with rating too high."""
    response = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 6}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
def test_submit_rating_unauthenticated(client, seed_driver):
    """Test rating submission without authentication."""
    response = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        json={"rating": 5}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
def test_rating_updates_driver_avg(client, student_headers, driver_headers, seed_driver, db_session):
    """Test that rating updates driver average."""
    # Submit rating
    response = client.post(
        f"/drivers/{seed_driver.id}/ratings",
        headers=student_headers,
        json={"rating": 5}
    )
    assert response.status_code == 201

    # Check updated driver avg
    driver_response = client.get(f"/drivers/{seed_driver.id}", headers=student_headers)
    assert driver_response.status_code == 200
    data = driver_response.json()
    assert float(data["avg_rating"]) == 5.0
    assert data["total_ratings"] == 1
