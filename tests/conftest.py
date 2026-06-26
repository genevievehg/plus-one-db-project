import pytest
from fastapi.testclient import TestClient

from main import app
from db.connection import get_connection
from db.auth import create_access_token, hash_password

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
        VALUES (%s,%s,%s,%s,%s,%s) 
        RETURNING id""", 
        ('test_event', 'test event for testing', 
        '2026-06-24 09:00:00', '2036-06-24 09:00:00', 1, 1)
    )
    id = cursor.fetchone()[0]
    conn.commit()
    yield id
    cursor.execute("DELETE FROM events WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture
def test_user():
    test_password = 'password123'
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO users 
        (email, user_password, user_name)
        VALUES (%s,%s,%s)
        RETURNING id""", ('test_email@email.com', 
        hash_password(test_password), 
        'test_user',))
    id = cursor.fetchone()[0]
    conn.commit()
    yield {'id': id, 
            'email': 'test_email@email.com', 
            'user_password': test_password,}
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture
def cleanup_users():
    """Collects users created directly through the API during a test
    so they can be removed."""
    created_users = []
    yield created_users
    if created_users:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM users WHERE id = ANY(%s)", (created_users,)
        )
        conn.commit()
        cursor.close()
        conn.close()

@pytest.fixture
def auth_headers():
    token = create_access_token(1)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def cleanup_rsvps():
    """Collects rsvps created directly through the API during a test
    so they can be removed."""
    created_rsvps = []
    yield created_rsvps
    if created_rsvps:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM rsvps WHERE id = ANY(%s)", (created_rsvps,)
        )
        conn.commit()
        cursor.close()
        conn.close()


@pytest.fixture
def sample_rsvp():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """ 
        INSERT INTO rsvps (attendee_id, event_id)
        VALUES (%s, %s)
        RETURNING id""", 
        (1, 4)
    )
    id = cursor.fetchone()[0]
    conn.commit()
    yield {'id': id,
           'event_id': 4}
    cursor.close()
    conn.close()