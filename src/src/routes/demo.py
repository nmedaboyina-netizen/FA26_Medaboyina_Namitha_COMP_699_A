from flask import Blueprint, flash, redirect, url_for
from src.database.db import get_db

bp = Blueprint("demo", __name__, url_prefix="/demo")

@bp.post("/load")
def load_demo():
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM evidence_events").fetchone()[0]
    if count:
        flash("Demo data was not loaded because evidence events already exist. Use your current records or reset the local demo database manually.", "error")
        return redirect(url_for("dashboard.index"))
    sample = [
        ("Witness observes vehicle", "2026-01-10T09:00", "2026-01-10T09:10", "North entrance", 10, "Witness"),
        ("Vehicle enters building", "2026-01-10T09:20", "2026-01-10T09:30", "Main entrance", 10, "Surveillance"),
        ("Vehicle leaves building", "2026-01-10T09:45", "2026-01-10T09:55", "South exit", 10, "Surveillance"),
    ]
    event_ids = []
    for event in sample:
        cur = db.execute("""INSERT INTO evidence_events
            (description,start_time,end_time,location,duration_minutes,source_type)
            VALUES (?,?,?,?,?,?)""", event)
        event_ids.append(cur.lastrowid)
    db.execute("""INSERT INTO event_relationships
        (event_id_1,event_id_2,relationship_type,description)
        VALUES (?,?,'BEFORE','Witness observation precedes entry')""", (event_ids[0], event_ids[1]))
    db.execute("""INSERT INTO event_relationships
        (event_id_1,event_id_2,relationship_type,description)
        VALUES (?,?,'BEFORE','Entry precedes departure')""", (event_ids[1], event_ids[2]))
    db.commit()
    flash("Three sample evidence events and two BEFORE constraints were loaded. Run timeline analysis to test the complete workflow.", "success")
    return redirect(url_for("dashboard.index"))
