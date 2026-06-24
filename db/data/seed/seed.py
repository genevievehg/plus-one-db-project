import json
from db.connection import get_connection
from db.data.normalisation import normalise_user_data, normalise_venue_data, normalise_event_data, normalise_rsvp_data

def drop_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email  VARCHAR(255) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def create_venues_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE venues (
    id SERIAL PRIMARY KEY,
    venue_name VARCHAR(255) UNIQUE NOT NULL,
    venue_address TEXT,
    capacity INT
    )""")
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def create_events_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE table events (
    id SERIAL PRIMARY KEY,
    title  VARCHAR(255) UNIQUE NOT NULL,
    event_description VARCHAR(255),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    organiser_id INT REFERENCES users(id),
    venue_id INT REFERENCES venues(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def create_rsvps_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE table rsvps (
    id SERIAL PRIMARY KEY,
    attendee_id INT REFERENCES users(id),
    event_id INT REFERENCES events(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
)   """)
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def seed_users_table(user_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""INSERT INTO users 
    (email, user_password, user_name) VALUES(%s,%s,%s)"""
    , user_data)
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def seed_venues_table(venue_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""INSERT INTO venues 
    (venue_name, venue_address, capacity) VALUES(%s,%s,%s)"""
    , venue_data)
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def seed_events_table(event_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""INSERT INTO events 
    (title, event_description, starts_at, ends_at, organiser_id, venue_id) VALUES(%s,%s,%s,%s,%s,%s)"""
    , event_data)
    
    conn.commit()

    cursor.close()
    conn.close()
    return 

def seed_rsvps_table(rsvp_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""INSERT INTO rsvps 
    (attendee_id, event_id) VALUES(%s,%s)"""
    , rsvp_data)
    
    conn.commit()

    cursor.close()
    conn.close()
    return 


drop_table('rsvps')
drop_table('events')
drop_table('venues')
drop_table('users')
create_users_table()
create_venues_table()
create_events_table()
create_rsvps_table()

with open('db/data/users.json', 'r') as file:
    user_data = json.load(file)
normalised_users = normalise_user_data(user_data)
seed_users_table(normalised_users)

with open('db/data/venues.json', 'r') as file:
    venue_data = json.load(file)
normalised_venues = normalise_venue_data(venue_data)
seed_venues_table(normalised_venues)

with open('db/data/events.json', 'r') as file:
    event_data = json.load(file)
normalised_events = normalise_event_data(event_data)
seed_events_table(normalised_events)

with open('db/data/rsvps.json', 'r') as file:
    rsvp_data = json.load(file)
normalised_rsvps = normalise_rsvp_data(rsvp_data)
seed_rsvps_table(normalised_rsvps)