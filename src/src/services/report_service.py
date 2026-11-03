from src.database.db import get_db

def save_analysis(status,summary,conflicts):
    db=get_db()
    cur=db.execute("INSERT INTO analysis_runs(status,summary) VALUES (?,?)",(status,summary))
    analysis_id=cur.lastrowid
    for c in conflicts:
        db.execute("""INSERT INTO analysis_conflicts
          (analysis_id,relationship_id,event_id_1,event_id_2,explanation)
          VALUES (?,?,?,?,?)""",(analysis_id,c.get("relationship_id"),c.get("event_id_1"),
          c.get("event_id_2"),c["explanation"]))
    db.commit()
    return analysis_id

def get_analysis(analysis_id):
    db=get_db()
    run=db.execute("SELECT * FROM analysis_runs WHERE analysis_id=?",(analysis_id,)).fetchone()
    conflicts=db.execute("SELECT * FROM analysis_conflicts WHERE analysis_id=?",(analysis_id,)).fetchall()
    return run,conflicts
