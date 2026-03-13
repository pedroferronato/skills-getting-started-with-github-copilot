import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

original_activities = copy.deepcopy(activities)

@pytest.fixture
def client():
    # Reset activities to original state
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    with TestClient(app) as c:
        yield c

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)

def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" == response.json()["message"]
    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]

def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    # Try again
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert response.status_code == 400
    assert "Student already signed up" == response.json()["detail"]

def test_signup_invalid_email(client):
    response = client.post("/activities/Chess Club/signup", params={"email": "test@gmail.com"})
    assert response.status_code == 400
    assert "Invalid email domain. Must be @mergington.edu" == response.json()["detail"]

def test_unregister_success(client):
    # First signup
    client.post("/activities/Chess Club/signup", params={"email": "test@mergington.edu"})
    # Then unregister
    response = client.delete("/activities/Chess Club/unregister", params={"email": "test@mergington.edu"})
    assert response.status_code == 200
    assert "Unregistered test@mergington.edu from Chess Club" == response.json()["message"]
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" not in data["Chess Club"]["participants"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/Nonexistent Activity/unregister", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" == response.json()["detail"]

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Chess Club/unregister", params={"email": "notsigned@mergington.edu"})
    assert response.status_code == 400
    assert "Student not signed up for this activity" == response.json()["detail"]

def test_unregister_invalid_email(client):
    response = client.delete("/activities/Chess Club/unregister", params={"email": "test@gmail.com"})
    assert response.status_code == 400
    assert "Invalid email domain. Must be @mergington.edu" == response.json()["detail"]