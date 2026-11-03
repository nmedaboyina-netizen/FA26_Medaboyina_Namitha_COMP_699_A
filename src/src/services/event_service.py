from src.database.db import get_db

def list_events():
    return get_db().execute("SELECT * FROM evidence_events ORDER BY start_time,event_id").fetchall()

def get_event(event_id):
    return get_db().execute("SELECT * FROM evidence_events WHERE event_id=?", (event_id,)).fetchone()

def create_event(e):
    db = get_db()
    cur = db.execute("""INSERT INTO evidence_events
      (description,start_time,end_time,location,duration_minutes,source_type)
      VALUES (?,?,?,?,?,?)""", (e["description"],e["start_time"],e["end_time"],
      e["location"],e["duration_minutes"],e["source_type"]))
    db.commit()
    return cur.lastrowid

def update_event(event_id,e):
    db=get_db()
    db.execute("""UPDATE evidence_events SET description=?,start_time=?,end_time=?,
      location=?,duration_minutes=?,source_type=? WHERE event_id=?""",
      (e["description"],e["start_time"],e["end_time"],e["location"],
       e["duration_minutes"],e["source_type"],event_id))
    db.commit()

def delete_event(event_id):
    db=get_db()
    db.execute("DELETE FROM evidence_events WHERE event_id=?", (event_id,))
    db.commit()
