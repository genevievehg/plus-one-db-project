from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from db.connection import get_connection
from db.auth import verify_password, create_access_token, hash_password, get_current_user

app = FastAPI()

class CredentialsRequest(BaseModel):
    email: str
    password: str

class User(BaseModel):
    email: str
    user_password: str
    user_name: str


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
    if not payload.email:
        raise HTTPException(status_code = 400, detail = 'Missing email')
    if not payload.password:
        raise HTTPException(status_code = 400, detail = 'Missing password')
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, user_password FROM users
            WHERE email = %s""",
            (payload.email,)
        )
        row = cur.fetchone()
        if row is None or not verify_password(payload.password, row[1]):
            raise HTTPException(status_code = 401, detail = "Invalid email or password")
        token = create_access_token(row[0])
        return {'token': token}

@app.post("/api/auth/register", status_code = 201)
def user_register(payload:User):
    if not payload.email:
        raise HTTPException(status_code = 400, detail = 'Missing email')
    if not payload.user_password:
        raise HTTPException(status_code = 400, detail = 'Missing password')
    if not payload.user_name:
        raise HTTPException(status_code = 400, detail = 'Name missing')
        
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * from users
            WHERE email = %s""",
            (payload.email,))
        row_1 = cur.fetchone()
        if row_1 is not None:
            raise HTTPException(status_code = 409, detail = "Email address already registered")
        
        hashed_password = hash_password(payload.user_password)
        cur.execute(
            """INSERT INTO users 
            (email, user_password, user_name) VALUES (%s,%s,%s)
            RETURNING id, created_at""",
            (payload.email, hashed_password, payload.user_name,)
        )
        row_2 = cur.fetchone()
        conn.commit()
        return {"user": {
        "id": row_2[0],
        "name": payload.user_name,
        "email": payload.email,
        "created_at": row_2[1]}}

@app.post("/api/events/{event_id}/rsvp", status_code = 201)
def user_rsvp(event_id: int, user_id = Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * from events
            WHERE id = %s""",
            (event_id,))
        row_1 = cur.fetchone()
        if row_1 is None:
            raise HTTPException(status_code = 404, detail = "Event does not exist")
        
        cur.execute(
            """SELECT * from rsvps
            WHERE attendee_id = %s AND event_id = %s""",
            (user_id, event_id,))
        row_1 = cur.fetchone()
        if row_1:
            raise HTTPException(status_code = 409, detail = "RSVP already exists")
        
        cur.execute("""INSERT INTO rsvps 
        (attendee_id, event_id)
        VALUES (%s, %s)
        RETURNING *""",
        (user_id, event_id,))
        row = cur.fetchone()
        conn.commit()
        return {"rsvp": {
        "id": row[0],
        "attendee_id": row[1],
        "event_id": row[2],
        "created_at": row[3]}}

@app.delete("/api/events/{event_id}/rsvp/me", status_code = 204)
def delete_rsvp(event_id: int, user_id = Depends(get_current_user)):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT * from rsvps
            WHERE event_id = %s and attendee_id = %s""",
            (event_id, user_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code = 404, detail = "RSVP does not exist")

        cur.execute(
            """DELETE from rsvps
            WHERE event_id = %s AND attendee_id = %s""",
            (event_id, user_id,))
        conn.commit()