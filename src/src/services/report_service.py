import json
from src.database.db import get_db


def save_analysis(status, summary, conflicts, events=None, relationships=None, alternatives=None):
    """Save the result and an immutable copy of the inputs used for this run."""
    db = get_db()
    cur = db.execute(
        """INSERT INTO analysis_runs
           (status, summary, event_snapshot, relationship_snapshot, alternatives_snapshot)
           VALUES (?, ?, ?, ?, ?)""",
        (status, summary,
         json.dumps([dict(row) for row in (events or [])]),
         json.dumps([dict(row) for row in (relationships or [])]),
         json.dumps(alternatives or []))
    )
    analysis_id = cur.lastrowid
    for conflict in conflicts:
        db.execute(
            """INSERT INTO analysis_conflicts
               (analysis_id, relationship_id, event_id_1, event_id_2, explanation)
               VALUES (?, ?, ?, ?, ?)""",
            (analysis_id, conflict.get("relationship_id"), conflict.get("event_id_1"),
             conflict.get("event_id_2"), conflict["explanation"])
        )
    db.commit()
    return analysis_id


def get_analysis(analysis_id):
    db = get_db()
    run = db.execute("SELECT * FROM analysis_runs WHERE analysis_id=?", (analysis_id,)).fetchone()
    conflicts = db.execute(
        "SELECT * FROM analysis_conflicts WHERE analysis_id=? ORDER BY conflict_id", (analysis_id,)
    ).fetchall()
    return run, conflicts


def get_analysis_snapshot(run):
    """Read the exact input state saved for a run; support older database records."""
    if run is None:
        return {"events": [], "relationships": [], "alternatives": []}
    keys = set(run.keys())
    if "event_snapshot" not in keys or not run["event_snapshot"]:
        from src.services.event_service import list_events
        from src.services.constraint_service import get_relationships
        return {"events": [dict(x) for x in list_events()],
                "relationships": [dict(x) for x in get_relationships()],
                "alternatives": []}
    return {
        "events": json.loads(run["event_snapshot"] or "[]"),
        "relationships": json.loads(run["relationship_snapshot"] or "[]"),
        "alternatives": json.loads(run["alternatives_snapshot"] or "[]")
    }
