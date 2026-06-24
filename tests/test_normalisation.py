from db.data.normalisation import normalise_user_data, normalise_venue_data, normalise_event_data, normalise_rsvp_data

sample_user_data = [{
    "name": "Alice Rahman",
    "email": "alice@example.com",
    "password": "password123"},
  {"name": "Bob Nguyen",
    "email": "bob@example.com",
    "password": "password123"}]

sample_venue_data = [{"name": "Nexus, University of Leeds",
    "address": "Discovery Way, Leeds, LS2 3AA",
    "capacity": 200},
  {"name": "Manchester Central Library",
    "address": "St Peter's Square, Manchester, M2 5PD",
    "capacity": 80}]

sample_event_data = [
  {"title": "Leeds Tech Meetup – June Edition",
    "description": "Monthly meetup for Leeds-based developers. Lightning talks and networking.",
    "starts_at": "2026-06-18T18:30:00+01:00",
    "ends_at": "2026-06-18T21:00:00+01:00",
    "organiser_id": 1,
    "venue_id": 1},
  {"title": "Intro to Machine Learning Workshop",
    "description": "Hands-on workshop covering perceptrons, neural networks, and classifiers using NumPy and PyTorch.",
    "starts_at": "2026-06-25T10:00:00+01:00",
    "ends_at": "2026-06-25T13:00:00+01:00",
    "organiser_id": 2,
    "venue_id": 3}]

sample_rsvp_data = [{ "attendee_id": 2, "event_id": 1 },
  { "attendee_id": 3, "event_id": 1 },
  { "attendee_id": 4, "event_id": 1 },
  { "attendee_id": 5, "event_id": 1 },
  { "attendee_id": 1, "event_id": 2 },
  { "attendee_id": 4, "event_id": 2 },
  { "attendee_id": 6, "event_id": 2 }]

def test_convert_user_data_result_is_list():
    assert type(normalise_user_data(sample_user_data)) == list

def test_convert_user_data_returns_list_of_tuples():
    result = normalise_user_data(sample_user_data)
    assert type(result[0]) == tuple

def test_convert_venue_data_result_is_list():
    assert type(normalise_venue_data(sample_venue_data)) == list

def test_convert_venue_data_returns_list_of_tuples():
    result = normalise_venue_data(sample_venue_data)
    assert type(result[0]) == tuple

def test_convert_event_data_result_is_list():
    assert type(normalise_event_data(sample_event_data)) == list

def test_convert_event_data_returns_list_of_tuples():
    result = normalise_event_data(sample_event_data)
    assert type(result[0]) == tuple

def test_convert_rsvp_data_result_is_list():
    assert type(normalise_rsvp_data(sample_rsvp_data)) == list

def test_convert_rsvp_data_returns_list_of_tuples():
    result = normalise_rsvp_data(sample_rsvp_data)
    assert type(result[0]) == tuple