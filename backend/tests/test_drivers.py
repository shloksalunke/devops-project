"""Driver endpoint tests."""
import pytest


@pytest.mark.asyncio
def test_list_drivers_authenticated(client, student_headers, seed_driver):
    """Test list drivers when authenticated."""
    response = client.get("/drivers", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
def test_list_drivers_unauthenticated(client):
    """Test list drivers without authentication."""
    response = client.get("/drivers")
    assert response.status_code == 403


@pytest.mark.asyncio
def test_filter_by_vehicle_type(client, student_headers, db_session):
    """Test filter drivers by vehicle type."""
    from app.models.driver import Driver
    from app.services.auth_service import hash_password

    # Add multiple drivers with different vehicle types
    for i, vtype in enumerate(["auto", "taxi", "car"]):
        driver = Driver(
            name=f"Driver {i}",
            phone=f"+91 98220 {i:05d}",
            email=f"driver{i}@test.com",
            hashed_password=hash_password("Driver@123"),
            vehicle_type=vtype
        )
        db_session.add(driver)
    db_session.commit()

    response = client.get("/drivers?vehicle_type=auto", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(d["vehicle_type"] == "auto" for d in data)


@pytest.mark.asyncio
def test_get_driver_detail(client, student_headers, seed_driver):
    """Test get driver details."""
    response = client.get(f"/drivers/{seed_driver.id}", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seed_driver.id)
    assert "ratings" in data


@pytest.mark.asyncio
def test_get_nonexistent_driver(client, student_headers):
    """Test get nonexistent driver."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/drivers/{fake_id}", headers=student_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
def test_log_contact(client, student_headers, seed_driver):
    """Test log driver contact."""
    response = client.post(f"/drivers/{seed_driver.id}/contacts", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Contact logged"
