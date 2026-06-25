import json
from db.auth import hash_password

#converts user data to usable list of tuples; corrects input order
def normalise_user_data(data_input):
    normalised_users =[]
    for user in data_input:
        name = user.get('name')
        email = user.get('email')
        hashed_password = hash_password(user.get('password'))
        normalised_users.append((email, hashed_password, name))
    return normalised_users


#converts venue data to usable list of tuples
def normalise_venue_data(data_input):
    normalised_venues =[]
    for venue in data_input:
        venue_name = venue.get('name')
        venue_address = venue.get('address')
        capacity = venue.get('capacity')
        normalised_venues.append((venue_name, venue_address, capacity))
    return normalised_venues


#converts event data to usable list of tuples
def normalise_event_data(data_input):
    normalised_events =[]
    for event in data_input:
        title = event.get('title')
        event_description = event.get('description')
        starts_at = event.get('starts_at')
        ends_at = event.get('ends_at')
        organiser_id = event.get('organiser_id')
        venue_id = event.get('venue_id')
        normalised_events.append((title, event_description, starts_at, ends_at, organiser_id, venue_id))
    return normalised_events


#converts rsvp data to usable list of tuples
def normalise_rsvp_data(data_input):
    normalised_rsvps =[]
    for rsvp in data_input:
        attendee_id = rsvp.get('attendee_id')
        event_id = rsvp.get('event_id')
        normalised_rsvps.append((attendee_id, event_id))
    return normalised_rsvps