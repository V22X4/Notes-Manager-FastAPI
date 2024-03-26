import pytest
import requests

API_URL = "http://localhost:8000"  # Update this with your API URL

@pytest.fixture
def auth_token():
    
    signup_data = {"username": "test_user", "password": "test_password"}
    requests.post(f"{API_URL}/api/auth/signup", json=signup_data)

    login_data = {"username": "test_user", "password": "test_password"}
    response = requests.post(f"{API_URL}/api/auth/login", data=login_data)
    return response.json()["access_token"]

def test_create_and_read_notes(auth_token):
    
    create_data = {"title": "Test Note", "content": "This is a test note"}
    create_response = requests.post(f"{API_URL}/api/notes", json=create_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert create_response.status_code == 200
    note_id = create_response.json()["_id"]

    read_response = requests.get(f"{API_URL}/api/notes/{note_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert read_response.status_code == 200
    assert read_response.json()["title"] == create_data["title"]
    assert read_response.json()["content"] == create_data["content"]

def test_update_note(auth_token):
    
    create_data = {"title": "Test Note", "content": "This is a test note"}
    create_response = requests.post(f"{API_URL}/api/notes", json=create_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert create_response.status_code == 200
    note_id = create_response.json()["_id"]

   
    update_data = {"title": "Updated Title"}
    update_response = requests.put(f"{API_URL}/api/notes/{note_id}", json=update_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == update_data["title"]

def test_delete_note(auth_token):
    
    create_data = {"title": "Test Note", "content": "This is a test note"}
    create_response = requests.post(f"{API_URL}/api/notes", json=create_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert create_response.status_code == 200
    note_id = create_response.json()["_id"]

    
    delete_response = requests.delete(f"{API_URL}/api/notes/{note_id}", headers={"Authorization": f"Bearer {auth_token}"})
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Note deleted successfully"

def test_share_note(auth_token):

    create_data = {"title": "Test Note", "content": "This is a test note"}
    create_response = requests.post(f"{API_URL}/api/notes", json=create_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert create_response.status_code == 200
    note_id = create_response.json()["_id"]

    share_data = {"share_with": "example_username"}
    share_response = requests.post(f"{API_URL}/api/notes/{note_id}/share", json=share_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert share_response.status_code == 200
    assert share_response.json()["shared_with"] == ["example_username"]

def test_search_notes(auth_token):

    create_data = {"title": "Test Note", "content": "This is a test note"}
    create_response = requests.post(f"{API_URL}/api/notes", json=create_data, headers={"Authorization": f"Bearer {auth_token}"})
    assert create_response.status_code == 200

    search_query = "test"
    search_response = requests.get(f"{API_URL}/api/search?q={search_query}", headers={"Authorization": f"Bearer {auth_token}"})
    assert search_response.status_code == 200
    assert len(search_response.json()) > 0
    
if __name__ == "__main__":
    pytest.main([__file__])
