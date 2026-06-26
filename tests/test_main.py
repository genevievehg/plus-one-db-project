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


def test_auth_login_returns_200(client, test_user):
    response = client.post('/api/auth/login', json={
            "email": test_user['email'],
            "password": test_user['user_password'],
        })
    assert response.status_code == 200

def test_auth_login_returns_401_with_invalid_credentials(client, test_user):
    response = client.post('/api/auth/login', json={
            "email": test_user['email'],
            "password": 'incorrect_password',})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    
def test_auth_login_returns_400_with_missing_email(client, test_user):
    response = client.post('/api/auth/login', json={
            "email": '',
            "password": test_user['user_password'],
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing email"

def test_auth_login_returns_400_with_missing_password(client, test_user):
    response = client.post('/api/auth/login', json={
            "email": test_user['email'],
            "password": '',
        })
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing password"

def test_user_register_returns_201_on_successful_registration(client, cleanup_users):
    response = client.post('/api/auth/register', json={
            'email': 'test_email@email.com',
            'user_password': 'test_password',
            'user_name': 'test_user_name',})
    body = response.json()
    assert response.status_code == 201
    cleanup_users.append(body["user"]['id'])

def test_user_register_returns_409_for_duplicate_email(client, test_user):
    response = client.post('/api/auth/register', json={
            'email': test_user['email'],
            'user_password': 'test_password',
            'user_name': 'test_user_name',})
    assert response.status_code == 409

def test_user_register_returns_400_for_missing_field(client):
    response = client.post('/api/auth/register', json={
            'email': '',
            'user_password': 'test_password',
            'user_name': 'test_user_name',})
    assert response.status_code == 400
#- Missing fields return a `400`