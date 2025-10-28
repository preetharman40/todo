# /tests/test_main.py
import pytest
from fastapi.testclient import TestClient

# We use pytest-asyncio for all tests
pytestmark = pytest.mark.asyncio

# --- Test 1: User Registration ---
def test_register_user(client: TestClient):
    # Send a request to the /register endpoint
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    # Check that it worked
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data
    
    # Check that you can't register the same user twice
    response_fail = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response_fail.status_code == 400
    assert "Username already registered" in response_fail.json()["detail"]


# --- Test 2: User Login ---
def test_login_user(client: TestClient):
    # First, create the user so we can log in
    client.post(
        "/register",
        json={"username": "testlogin", "password": "testpassword"}
    )
    
    # Now, try to log in
    response = client.post(
        "/login",
        data={"username": "testlogin", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Test with wrong password
    response_fail = client.post(
        "/login",
        data={"username": "testlogin", "password": "wrongpassword"}
    )
    assert response_fail.status_code == 401
    assert "Incorrect username or password" in response_fail.json()["detail"]


# --- Test 3: The Full Task Lifecycle (Authenticated Test) ---
def test_create_and_get_tasks(client: TestClient):
    # 1. Register a new user
    client.post(
        "/register",
        json={"username": "taskuser", "password": "taskpass"}
    )
    
    # 2. Log in to get a token
    login_response = client.post(
        "/login",
        data={"username": "taskuser", "password": "taskpass"}
    )
    token = login_response.json()["access_token"]
    
    # 3. Create the authorization headers
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Try to get tasks (should be empty)
    response_get_empty = client.get("/tasks/", headers=headers)
    assert response_get_empty.status_code == 200
    assert response_get_empty.json() == [] # No tasks yet
    
    # 5. Create a new task
    response_create = client.post(
        "/tasks",
        headers=headers,
        json={"title": "My first task", "description": "Test this"}
    )
    assert response_create.status_code == 200
    task_data = response_create.json()
    assert task_data["title"] == "My first task"
    
    # 6. Get tasks again (should now have one)
    response_get_one = client.get("/tasks/", headers=headers)
    assert response_get_one.status_code == 200
    assert len(response_get_one.json()) == 1
    assert response_get_one.json()[0]["title"] == "My first task"