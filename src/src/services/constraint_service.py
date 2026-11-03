from src.database.db import get_db

def list_relationships():
    return get_db().execute("""SELECT r.*,a.description event_a,b.description event_b
      FROM event_relationships r JOIN evidence_events a ON a.event_id=r.event_id_1
      JOIN evidence_events b ON b.event_id=r.event_id_2 ORDER BY r.relationship_id""").fetchall()

def get_relationships():
    return get_db().execute("SELECT * FROM event_relationships").fetchall()

def add_before(a,b,description=""):
    if a == b:
        raise ValueError("An event cannot be before itself.")
    db=get_db()
    rows=db.execute("SELECT event_id FROM evidence_events WHERE event_id IN (?,?)",(a,b)).fetchall()
    if len(rows) != 2:
        raise ValueError("Select two existing evidence events.")
    try:
        cur=db.execute("INSERT INTO event_relationships(event_id_1,event_id_2,relationship_type,description) VALUES (?,?,'BEFORE',?)",(a,b,description))
        db.commit()
        return cur.lastrowid
    except Exception as exc:
        db.rollback()
        raise ValueError("This relationship already exists or is invalid.") from exc
