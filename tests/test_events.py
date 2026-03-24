import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models 
from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def event_payload():
    return {
        "date_venue": "2024-07-18",
        "time_venue_utc": "18:30:00",
        "sport_name": "Football",
        "home_team_name": "Salzburg",
        "away_team_name": "Sturm",
        "status": "played",
    }


# --- POST /events/ ---


def test_create_event_returns_201(client, event_payload):
    """
    Sends a POST request with a new event. 
    Checks that the server responds with status 201 Created.
    """
    response = client.post("/events/", json=event_payload)
    assert response.status_code == 201


def test_create_event_response_fields(client, event_payload):
    """
    Checks that the response body contains all expected fields and values.
    """
    data = client.post("/events/", json=event_payload).json()
    assert data["date_venue"] == "2024-07-18"
    assert data["time_venue_utc"] == "18:30:00"
    assert data["sport"]["name"] == "Football"
    assert data["home_team"]["name"] == "Salzburg"
    assert data["away_team"]["name"] == "Sturm"
    assert data["status"] == "played"


def test_create_event_auto_creates_sport_and_teams(client, event_payload):
    """Sport and teams that don't exist yet should be created on the fly."""
    data = client.post("/events/", json=event_payload).json()
    assert data["sport"]["id"] is not None
    assert data["home_team"]["id"] is not None
    assert data["away_team"]["id"] is not None


def test_create_two_events_reuse_same_sport(client, event_payload):
    """POSTing two events with the same sport should not create duplicate sport rows."""
    payload2 = {**event_payload, "home_team_name": "KAC", "away_team_name": "Capitals"}
    r1 = client.post("/events/", json=event_payload).json()
    r2 = client.post("/events/", json=payload2).json()
    assert r1["sport"]["id"] == r2["sport"]["id"]


# --- GET /events/ ---


def test_get_events_empty(client):
    response = client.get("/events/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_events_returns_created_event(client, event_payload):
    client.post("/events/", json=event_payload)
    events = client.get("/events/").json()
    assert len(events) == 1
    assert events[0]["sport"]["name"] == "Football"


def test_get_events_uses_single_query(client, event_payload):
    """All relationships should be eagerly loaded """
    payload2 = {**event_payload, "home_team_name": "KAC", "away_team_name": "Capitals", "sport_name": "Ice Hockey"}
    client.post("/events/", json=event_payload)
    client.post("/events/", json=payload2)
    events = client.get("/events/").json()
    assert len(events) == 2

    for event in events:
        assert "sport" in event
        assert "home_team" in event
        assert "away_team" in event


def test_get_events_sorted_newest_first(client, event_payload):
    older = {**event_payload, "date_venue": "2023-01-01"}
    newer = {**event_payload, "date_venue": "2025-06-01", "home_team_name": "KAC", "away_team_name": "Capitals"}
    client.post("/events/", json=older)
    client.post("/events/", json=newer)
    events = client.get("/events/").json()
    assert events[0]["date_venue"] == "2025-06-01"
    assert events[1]["date_venue"] == "2023-01-01"


def test_get_events_filter_by_sport(client, event_payload):
    hockey = {**event_payload, "sport_name": "Ice Hockey", "home_team_name": "KAC", "away_team_name": "Capitals"}
    client.post("/events/", json=event_payload)
    client.post("/events/", json=hockey)
    events = client.get("/events/?sport=Football").json()
    assert len(events) == 1
    assert events[0]["sport"]["name"] == "Football"


# --- GET /events/{id} ---


def test_get_event_by_id(client, event_payload):
    created = client.post("/events/", json=event_payload).json()
    response = client.get(f"/events/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_event_not_found(client):
    response = client.get("/events/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"
