def add_event(client, description, start, end):
    return client.post("/events/add", data={
        "description": description, "start_time": start, "end_time": end,
        "location": "Test location", "duration_minutes": "10", "source_type": "Witness"
    }, follow_redirects=True)

def test_end_to_end_consistent_workflow(client):
    add_event(client, "Event A", "2026-01-10T09:00", "2026-01-10T09:10")
    add_event(client, "Event B", "2026-01-10T09:20", "2026-01-10T09:30")
    add_event(client, "Event C", "2026-01-10T09:40", "2026-01-10T09:50")
    client.post("/constraints/add-before", data={"event_a": "1", "event_b": "2"})
    client.post("/constraints/add-before", data={"event_a": "2", "event_b": "3"})
    response = client.post("/analysis/run", follow_redirects=True)
    assert response.status_code == 200
    assert b"CONSISTENT" in response.data
    assert b"Candidate alternative event orders" in response.data
    with client.application.app_context():
        from src.database.db import get_db
        assert get_db().execute("SELECT COUNT(*) FROM evidence_events").fetchone()[0] == 3
        assert get_db().execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0] == 1

def test_end_to_end_temporal_conflict(client):
    add_event(client, "Event A", "2026-01-10T09:00", "2026-01-10T09:30")
    add_event(client, "Event B", "2026-01-10T09:20", "2026-01-10T09:40")
    client.post("/constraints/add-before", data={"event_a": "1", "event_b": "2"})
    response = client.post("/analysis/run", follow_redirects=True)
    assert b"INCONSISTENT" in response.data
    assert b"BEFORE rule violated" in response.data
    assert b"No alternative order is displayed" in response.data

def test_demo_data_loads_and_is_persisted(client):
    response = client.post("/demo/load", follow_redirects=True)
    assert response.status_code == 200
    assert b"Three sample evidence events" in response.data
    response = client.post("/analysis/run", follow_redirects=True)
    assert b"CONSISTENT" in response.data

def test_invalid_event_is_not_saved(client):
    response = client.post("/events/add", data={
        "description": "", "start_time": "not-a-date", "end_time": "2026-01-10T09:00",
        "location": "", "duration_minutes": "-2"
    }, follow_redirects=True)
    assert b"Event description is required" in response.data
    assert b"Enter valid start and end" in response.data
    with client.application.app_context():
        from src.database.db import get_db
        assert get_db().execute("SELECT COUNT(*) FROM evidence_events").fetchone()[0] == 0

def test_relationship_cannot_reference_same_event(client):
    add_event(client, "Event A", "2026-01-10T09:00", "2026-01-10T09:10")
    response = client.post("/constraints/add-before", data={"event_a": "1", "event_b": "1"}, follow_redirects=True)
    assert b"An event cannot be before itself" in response.data
