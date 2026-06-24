from starlette.testclient import TestClient as TestClient

def test_get_events_returns_all_events(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()['Events'] 
    assert type(events) == list

def test_get_event_by_id_returns_event(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")
    assert response.status_code == 200
    #further check here

def test_get_event_with_nonexisting_id_returns_404(client):
    response = client.get(f"/api/events/999")
    assert response.status_code == 404

def test_get_event_with_invalid_id_returns_400(client):
    response = client.get(f"/api/events/two")
    assert response.status_code == 400

