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

def test_user_rsvp_returns_201_for_authorised_user(client, auth_headers, cleanup_rsvps):
    response = client.post('/api/events/1/rsvp', headers = auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body['rsvp']['attendee_id'] == 1
    assert body['rsvp']['event_id'] == 1
    cleanup_rsvps.append(body['rsvp']['id'])

def test_user_rsvp_returns_401_for_unauthorised_user(client):
    response = client.post('/api/events/2/rsvp')
    assert response.status_code == 401

def test_user_rsvp_returns_404_for_unknown_event_id(client, auth_headers):
    response = client.post('/api/events/99/rsvp', headers = auth_headers)
    assert response.status_code == 404
    
def test_user_rsvp_returns_409_for_duplicate_rsvp(client, auth_headers):
    response = client.post('/api/events/2/rsvp', headers = auth_headers)
    assert response.status_code == 409

def test_delete_rsvp_returns_204(client, auth_headers, sample_rsvp):
    response = client.delete(f'/api/events/{sample_rsvp['event_id']}/rsvp/me', headers = auth_headers)
    assert response.status_code == 204

def test_delete_rsvp_without_authorsiation_returns_401(client):
    response = client.delete('/api/events/2/rsvp/me')
    assert response.status_code == 401

def test_delete_nonexisting_rsvp_returns_404(client, auth_headers):
    response = client.delete('/api/events/1/rsvp/me', headers = auth_headers)
    assert response.status_code == 404

def test_create_event_returns_201(client, auth_headers, cleanup_events):
    response = client.post('/api/events', headers = auth_headers, json={
            'title': 'test_title', 
            'description': 'test_event_description', 
            'starts_at': '2026-06-24 09:00:00', 
            'ends_at': '2036-06-24 09:00:00',
            'venue_id': 1,})
    assert response.status_code == 201
    body = response.json()
    assert body['Event']['organiser_id'] == 1
    cleanup_events.append(body['Event']['id'])


def test_create_event_without_authorisation_returns_401(client):
    response = client.post('/api/events', json={
            'title': 'test_title', 
            'description': 'test_event_description', 
            'starts_at': '2026-06-24 09:00:00', 
            'ends_at': '2036-06-24 09:00:00', 
            'organiser_id': 1, 
            'venue_id': 1,})
    assert response.status_code == 401
    
def test_create_event_with_missing_field_returns_400(client, auth_headers):
    response = client.post('/api/events', headers = auth_headers, json={
            'title': 'test_title', 
            'description': '', 
            'starts_at': '2026-06-24 09:00:00', 
            'ends_at': '2036-06-24 09:00:00', 
            'organiser_id': 1, 
            'venue_id': 1,})
    assert response.status_code == 400

def test_create_event_with_invalid_date_returns_400(client, auth_headers):
    response = client.post('/api/events', headers = auth_headers, json={
            'title': 'test_title', 
            'description': 'test_event_description', 
            'starts_at': '2036-06-24 09:00:00', 
            'ends_at': 'June 24th 1pm', 
            'organiser_id': 1, 
            'venue_id': 1,})
    assert response.status_code == 400

def test_update_event_returns_200(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'description': 'test_event_description',
            'venue_id': 1,})
    assert response.status_code == 200
    body = response.json()
    assert body["Event"]["description"] == 'test_event_description'
    assert body["Event"]["starts_at"] == '2026-06-18T18:30:00+01:00'
    assert body["Event"]["ends_at"] == '2026-06-18T21:00:00+01:00'


def test_update_event_returns_401_with_invalid_credentials(client):
    response = client.patch('/api/events/1', json={ 
            'description': 'test_event_description',
            'venue_id': 1,})
    assert response.status_code == 401

def test_update_event_returns_403_with_incorrect_user(client, auth_headers):
    response = client.patch('/api/events/2', headers = auth_headers, json={ 
            'description': 'test_event_description',
            'venue_id': 1,})
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden. Invalid user."

def test_update_event_returns_404_with_unknown_event(client, auth_headers):
    response = client.patch('/api/events/101', headers = auth_headers, json={ 
            'description': 'test_event_description',})
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

def test_update_event_returns_400_with_invalid_starts_at_format(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'starts_at': '9am',})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date format"

def test_update_event_returns_400_with_invalid_ends_at_format(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'ends_at': 'June 30th 9pm',})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date format"

def test_update_event_returns_400_with_ends_at_before_starts_at_both_provided(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'starts_at': '2026-06-18 18:30:00',
            'ends_at': '2026-06-17 20:30:00',})
    assert response.status_code == 400
    assert response.json()["detail"] == "Event start time must be before end time"

def test_update_event_returns_400_with_ends_at_before_starts_at_starts_at_provided(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'starts_at': '2026-06-19 18:30:00',})
    assert response.status_code == 400
    assert response.json()["detail"] == "Event start time must be before end time"

def test_update_event_returns_400_with_ends_at_before_starts_at_ends_at_provided(client, auth_headers):
    response = client.patch('/api/events/1', headers = auth_headers, json={ 
            'ends_at': '2026-06-17 18:30:00',})
    assert response.status_code == 400
    assert response.json()["detail"] == "Event start time must be before end time"
    
def test_get_rsvps_for_events_returns_200(client, auth_headers):
    response = client.get("/api/events/7/attendees", headers = auth_headers)
    assert response.status_code == 200
    events = response.json()['Attendees'] 
    assert events == [{'id': 4,
        'name': 'David Okafor',
        'email': 'david@example.com'},
        {'id': 6,
        'name': 'Frank Liu',
        'email': 'frank@example.com'}]

def test_get_rsvps_with_invalid_token_returns_401(client):
    response = client.get("/api/events/7/attendees")
    assert response.status_code == 401

def test_get_rsvps_with_user_who_is_not_organiser_returns_403(client, auth_headers):
    response = client.get("/api/events/2/attendees", headers = auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden. Must be event organiser."

def test_get_rsvps_for_nonexistent_event_returns_404(client, auth_headers):
    response = client.get("/api/events/101/attendees", headers = auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Event does not exist"
