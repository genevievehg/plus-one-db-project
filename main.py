from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
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


@app.get("/api/health")
def get_health():
    return {"Status": "healthy"}

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

@app.post("/api/events", status_code = 201)
def create_event(payload: dict, user_id = Depends(get_current_user)):
    event_title = payload.get('title')
    event_description = payload.get('description')
    starts_at = payload.get('starts_at')
    ends_at = payload.get('ends_at')
    venue_id = payload.get('venue_id')

    try:
        datetime.strptime(starts_at, "%Y-%m-%d %H:%M:%S")
    except:
        raise HTTPException(status_code = 400, detail = "Invalid date format")
    try:
        datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S")
    except:
        raise HTTPException(status_code = 400, detail = "Invalid date format")
  

    if not event_title:
        raise HTTPException(status_code = 400, detail = "Missing data. All fields required")
    if not event_description:
        raise HTTPException(status_code = 400, detail = "Missing data. All fields required")
    if not starts_at:
        raise HTTPException(status_code = 400, detail = "Missing data. All fields required")
    if not ends_at:
        raise HTTPException(status_code = 400, detail = "Missing data. All fields required")
    if not venue_id:
        raise HTTPException(status_code = 400, detail = "Missing data. All fields required")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO events (title, 
    event_description, starts_at, ends_at, organiser_id, venue_id)
    VALUES (%s,%s,%s,%s,%s,%s)
    RETURNING id, created_at""",
    (event_title, event_description, starts_at, ends_at, user_id, venue_id,))
    row = cursor.fetchone()
    id = row[0]
    created_at = row[1]
    conn.commit()
    cursor.close()
    conn.close()
    return {"Event":{"id": id,
      "title": event_title,
      "description": event_description,
      "starts_at": starts_at,
      "ends_at": ends_at,
      "venue_id": venue_id,
      "organiser_id": user_id,
      "created_at": created_at}}

@app.patch("/api/events/{event_id}")
def update_event(payload: dict, event_id: int, user_id = Depends(get_current_user)):
    event_title = payload.get('title')
    event_description = payload.get('description')
    starts_at = payload.get('starts_at')
    ends_at = payload.get('ends_at')
    venue_id = payload.get('venue_id')

    if starts_at:
        try:
            datetime.strptime(starts_at, "%Y-%m-%d %H:%M:%S")
        except:
            raise HTTPException(status_code = 400, detail = "Invalid date format")
    if ends_at:
        try:
            datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S")
        except:
            raise HTTPException(status_code = 400, detail = "Invalid date format")
    
    if starts_at and ends_at:
        if datetime.strptime(starts_at, "%Y-%m-%d %H:%M:%S") > datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S"):
            raise HTTPException(status_code = 400, detail = "Event start time must be before end time")
    conn = get_connection()

    if starts_at is not None and ends_at is None:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * from events
                WHERE id = %s""",
                (event_id,))
            ends_at = cur.fetchone()[4]
            if datetime.strptime(starts_at, "%Y-%m-%d %H:%M:%S") > ends_at.replace(tzinfo=None):
                raise HTTPException(status_code = 400, detail = "Event start time must be before end time")
    
    if starts_at is None and ends_at is not None:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * from events
                WHERE id = %s""",
                (event_id,))
            starts_at = cur.fetchone()[3]
            if starts_at.replace(tzinfo=None) > datetime.strptime(ends_at, "%Y-%m-%d %H:%M:%S"):
                raise HTTPException(status_code = 400, detail = "Event start time must be before end time")

    with conn.cursor() as cur:
        cur.execute(
            """SELECT * from events
            WHERE id = %s""",
            (event_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code = 404, detail = "Event not found")

    with conn.cursor() as cur:
        cur.execute(
            """SELECT * from events
            WHERE id = %s and organiser_id = %s""",
            (event_id, user_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code = 403, detail = "Forbidden. Invalid user.")

    if event_title is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE events 
        SET title = %s
        WHERE id = %s AND organiser_id = %s""",
        (event_title, event_id, user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    if event_description is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE events 
        SET event_description = %s
        WHERE id = %s AND organiser_id = %s""",
        (event_description, event_id, user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    if starts_at is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE events 
        SET starts_at = %s
        WHERE id = %s AND organiser_id = %s""",
        (starts_at, event_id, user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    if ends_at is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE events 
        SET ends_at = %s
        WHERE id = %s AND organiser_id = %s""",
        (ends_at, event_id, user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    
    if venue_id is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE events 
        SET venue_id = %s
        WHERE id = %s AND organiser_id = %s""",
        (venue_id, event_id, user_id,))
        conn.commit()
        cursor.close()
        conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT * FROM events
            WHERE events.id = %s
            """,
            (event_id,),)
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"Event": {"id": row[0], 
        "title": row[1], 
        "description": row[2],
        "starts_at": row[3], 
        "ends_at": row[4], 
        "venue_id": row[5],
        "organiser_id": row[6],
        "created_at": row[7],
    }}

@app.get("/api/events/{event_id}/attendees")
def get_attendees_for_event(event_id, user_id = Depends(get_current_user)):

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""SELECT *
            FROM events
            WHERE id = %s""",
            (event_id,),)
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code = 404, detail = "Event does not exist")

    with conn.cursor() as cur:
        cur.execute("""SELECT *
            FROM events
            WHERE id = %s and organiser_id = %s""",
            (event_id, user_id,),)
        rows = cur.fetchall()
        if rows == []:
            raise HTTPException(status_code = 403, detail = "Forbidden. Must be event organiser.")

    with conn.cursor() as cur:
        cur.execute("""SELECT users.id AS id, users.user_name AS name, 
            users.email AS email
            FROM rsvps
            INNER JOIN users on users.id = rsvps.attendee_id
            WHERE rsvps.event_id = %s""",
            (event_id,),)
        columns = [desc[0] for desc in cur.description]    
        rows = cur.fetchall()
        
        conn.close()
        return {"Attendees": [dict(zip(columns, row)) for row in rows]}

@app.get("/api/user/me/events")
def get_user_events(user_id = Depends(get_current_user)):

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""SELECT 
            events.id, 
            events.title, 
            events.starts_at, 
            rsvps.created_at AS rsvp_date, 
            RANK() OVER  
            (ORDER BY events.starts_at) AS event_rank,
            COUNT(*) OVER () AS total_rsvps 
            FROM rsvps 
            INNER JOIN events on rsvps.event_id = events.id  
            WHERE attendee_id = %s""",
            (user_id,),)
        columns = [desc[0] for desc in cur.description]    
        rows = cur.fetchall()
        
        conn.close()
        return {"Events": [dict(zip(columns, row)) for row in rows]}