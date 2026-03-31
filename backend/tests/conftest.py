"""Test configuration and fixtures."""
import pytest
import pytest_asyncio
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.database import Base, get_db
from app.services.auth_service import hash_password
from app.models.user import User
from app.models.driver import Driver


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def override_get_db(db_session):
    """Override get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db):
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def registered_student(db_session):
    """Create a registered student user."""
    student = User(
        name="Test Student",
        email="student@test.com",
        hashed_password=hash_password("Student@123"),
        role="student"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def student_headers(client, db_session):
    """Get authentication headers for a student."""
    # Create student if not exists
    student = db_session.query(User).filter(User.email == "student@test.com").first()
    if not student:
        student = User(
            name="Test Student",
            email="student@test.com",
            hashed_password=hash_password("Student@123"),
            role="student"
        )
        db_session.add(student)
        db_session.commit()

    # Login
    response = client.post("/auth/login", json={"email": "student@test.com", "password": "Student@123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db_session):
    """Get authentication headers for an admin."""
    admin = db_session.query(User).filter(User.email == "admin@test.com").first()
    if not admin:
        admin = User(
            name="Admin User",
            email="admin@test.com",
            hashed_password=hash_password("Admin@123"),
            role="admin"
        )
        db_session.add(admin)
        db_session.commit()

    response = client.post("/auth/login", json={"email": "admin@test.com", "password": "Admin@123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def driver_headers(client, db_session):
    """Get authentication headers for a driver."""
    driver = db_session.query(Driver).filter(Driver.email == "driver@test.com").first()
    if not driver:
        driver = Driver(
            name="Test Driver",
            phone="+91 98220 00000",
            email="driver@test.com",
            hashed_password=hash_password("Driver@123"),
            vehicle_type="auto",
            vehicle_details="Test Auto"
        )
        db_session.add(driver)
        db_session.commit()

    response = client.post("/auth/login", json={"email": "driver@test.com", "password": "Driver@123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_driver(db_session):
    """Create a test driver."""
    driver = Driver(
        name="Seed Driver",
        phone="+91 98220 99999",
        email="seeddriver@test.com",
        hashed_password=hash_password("Driver@123"),
        vehicle_type="taxi",
        vehicle_details="Test Taxi"
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)
    return driver
