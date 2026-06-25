from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db.connection import get_connection
from db.auth import verify_password, create_access_token

app = FastAPI()

class CredentialsRequest(BaseModel):
    email: str
    password: str


@app.get("/api/events")
def get_events():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT events.id, events.title, 
    events.starts_at, events.ends_at, 
    venues.venue_name AS location
    FROM events 
    FULL JOIN venues ON events.venue_id = venues.id
    ORDER BY events.title""")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"Events":[dict(zip(columns, row)) for row in rows]}

@app.get("/api/events/{event_id}")
def get_event(event_id: str):

    if event_id.isdigit() is False:
        raise HTTPException(
            status_code = 400,
            detail = {'code': 'INVALID', 'message': 'Event id must be an integer'})
        
    
    event_id_int = int(event_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT events.id AS id, events.title AS title, 
            events.event_description, events.starts_at, 
            events.ends_at, venues.venue_name,
            venues.venue_address, venues.capacity, events.created_at
            FROM events
            INNER JOIN venues on events.venue_id = venues.id
            WHERE events.id = %s
            """,
            (event_id_int,),)
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code = 404,
            detail = {'code': 'NOT FOUND', 'message': 'Event not found'}
            )
    cursor.close()
    conn.close()
    return {"Event": {"id": row[0], "title": row[1], "event_description": row[2],
        "starts_at": row[3], "ends_at": row[4], "location": row[5], "address": row[6],
        "capacity": row[7], "created_at": row[8],
    }}

@app.post("/api/auth/login")
def user_login(payload:CredentialsRequest):
    if payload.email == '':
        raise HTTPException(status_code = 400, detail = 'Missing email')
    if payload.password == '':
        raise HTTPException(status_code = 400, detail = 'Missing password')
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, user_password FROM users WHERE email = %s",
            (payload.email,)
        )
        row = cur.fetchone()
        if row is None or not verify_password(payload.password, row[1]):
            raise HTTPException(status_code = 401, detail = "Invalid email or password")
        token = create_access_token(row[0])
        return {'access_token': token, 'token_type': 'bearer'}
