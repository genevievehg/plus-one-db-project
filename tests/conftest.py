import pytest
from fastapi.testclient import TestClient

from main import app
from db.connection import get_connection

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_event():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """ 
        INSERT INTO events (title, event_description, 
        starts_at, ends_at, organiser_id, venue_id)
        VALUES ('test_event', 'test event for testing', 
        '2026-06-24 09:00:00', '2036-06-24 09:00:00', 1, 1)
        RETURNING id
        """
    )
    id = cursor.fetchone()[0]
    conn.commit()
    yield id
    cursor.execute("DELETE FROM events WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
