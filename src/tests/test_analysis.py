def add(client,desc,start,end):
    return client.post("/events/add",data={"description":desc,"start_time":start,"end_time":end,"location":"A","duration_minutes":"10","source_type":"Other"},follow_redirects=True)

def test_consistent_before_rule(client):
    add(client,"A","2026-01-10T09:00","2026-01-10T09:10")
    add(client,"B","2026-01-10T09:20","2026-01-10T09:30")
    client.post("/constraints/add-before",data={"event_a":"1","event_b":"2"})
    r=client.post("/analysis/run",follow_redirects=True)
    assert b"CONSISTENT" in r.data

def test_conflict_reported(client):
    add(client,"A","2026-01-10T09:00","2026-01-10T09:30")
    add(client,"B","2026-01-10T09:20","2026-01-10T09:40")
    client.post("/constraints/add-before",data={"event_a":"1","event_b":"2"})
    r=client.post("/analysis/run",follow_redirects=True)
    assert b"INCONSISTENT" in r.data
    assert b"BEFORE rule violated" in r.data
