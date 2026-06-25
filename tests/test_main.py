from starlette.testclient import TestClient as TestClient

def test_get_events_returns_all_events(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()['Events'] 
    assert type(events) == list

def test_get_event_by_id_returns_event(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")
    assert response.status_code == 200

def test_get_event_with_nonexisting_id_returns_404(client):
    response = client.get(f"/api/events/999")
    assert response.status_code == 404

def test_get_event_with_invalid_id_returns_400(client):
    response = client.get(f"/api/events/two")
    assert response.status_code == 400


def test_auth_login_returns_token(client, test_user):
    response = client.post('/api/auth/login', json={
            "email": test_user['email'],
            "password": test_user['user_password'],
        })
    assert response.status_code == 200

def test_auth_login_returns_401_with_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
            "email": 'test_email@email.com',
            "password": 'test_password',
        })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    
def test_auth_login_returns_400_with_missing_email(client):
    response = client.post('/api/auth/login', json={
            "email": '',
            "password": 'test_password',
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing email"

def test_auth_login_returns_400_with_missing_password(client):
    response = client.post('/api/auth/login', json={
            "email": 'test_email@email.com',
            "password": '',
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing password"