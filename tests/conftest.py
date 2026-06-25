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


#@pytest.fixture
#def auth_headers():
 #   token = create_access_token(1)
 #   return {'Authorisation': f'Bearer {token}'}