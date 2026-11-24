import json


def add_event(client, description, start, end):
    return client.post("/events/add", data={
        "description": description, "start_time": start, "end_time": end,
        "location": "Test location", "duration_minutes": "10", "source_type": "Witness"
    }, follow_redirects=True)


def test_analysis_result_keeps_original_event_snapshot(client):
    add_event(client, "Original event A", "2026-01-10T09:00", "2026-01-10T09:10")
    add_event(client, "Original event B", "2026-01-10T09:20", "2026-01-10T09:30")
    client.post("/constraints/add-before", data={"event_a": "1", "event_b": "2"})
    response = client.post("/analysis/run")
    analysis_url = response.headers["Location"]

    client.post("/events/1/edit", data={
        "description": "Edited event A", "start_time": "2026-01-10T09:00",
        "end_time": "2026-01-10T09:15", "location": "Updated location",
        "duration_minutes": "15", "source_type": "Witness"
    }, follow_redirects=True)

    result = client.get(analysis_url)
    assert b"Original event A" in result.data
    assert b"Edited event A" not in result.data


def test_analysis_json_export_contains_saved_snapshot(client):
    add_event(client, "Export event A", "2026-01-10T09:00", "2026-01-10T09:10")
    response = client.post("/analysis/run")
    analysis_id = response.headers["Location"].rstrip("/").split("/")[-1]
    exported = client.get(f"/analysis/{analysis_id}/export")
    assert exported.status_code == 200
    payload = json.loads(exported.data)
    assert payload["status"] == "CONSISTENT"
    assert payload["events"][0]["description"] == "Export event A"
    assert "candidate_alternative_orders" in payload
