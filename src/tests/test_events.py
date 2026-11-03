def payload(**changes):
    data={"description":"Witness observation","start_time":"2026-01-10T09:00","end_time":"2026-01-10T09:15","location":"A","duration_minutes":"15","source_type":"Witness"}
    data.update(changes); return data

def test_event_crud(client):
    r=client.post("/events/add",data=payload(),follow_redirects=True)
    assert r.status_code==200 and b"Witness observation" in r.data
    r=client.post("/events/1/edit",data=payload(description="Updated"),follow_redirects=True)
    assert b"Updated" in r.data
    r=client.post("/events/1/delete",follow_redirects=True)
    assert b"Updated" not in r.data

def test_invalid_time_range_rejected(client):
    r=client.post("/events/add",data=payload(end_time="2026-01-10T08:00"),follow_redirects=True)
    assert b"End time must" in r.data
