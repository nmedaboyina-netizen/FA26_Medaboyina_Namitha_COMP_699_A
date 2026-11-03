import io

def test_json_import_and_export(client):
    payload=b'[{"description":"Imported","start_time":"2026-01-10T09:00","end_time":"2026-01-10T09:10","location":"Lab","duration_minutes":10}]'
    r=client.post("/data/import",data={"file":(io.BytesIO(payload),"events.json")},content_type="multipart/form-data",follow_redirects=True)
    assert b"Imported 1 evidence events" in r.data
    assert client.get("/data/export/json").mimetype=="application/json"
