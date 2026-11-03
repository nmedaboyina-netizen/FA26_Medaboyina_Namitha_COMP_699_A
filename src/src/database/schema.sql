CREATE TABLE IF NOT EXISTS evidence_events (
 event_id INTEGER PRIMARY KEY AUTOINCREMENT,
 description TEXT NOT NULL,
 start_time TEXT NOT NULL,
 end_time TEXT NOT NULL,
 location TEXT NOT NULL,
 duration_minutes REAL NOT NULL CHECK(duration_minutes >= 0),
 source_type TEXT NOT NULL DEFAULT 'Other',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK(end_time >= start_time)
);
CREATE TABLE IF NOT EXISTS event_relationships (
 relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_id_1 INTEGER NOT NULL REFERENCES evidence_events(event_id) ON DELETE CASCADE,
 event_id_2 INTEGER NOT NULL REFERENCES evidence_events(event_id) ON DELETE CASCADE,
 relationship_type TEXT NOT NULL CHECK(relationship_type IN ('BEFORE')),
 description TEXT DEFAULT '',
 CHECK(event_id_1 <> event_id_2),
 UNIQUE(event_id_1,event_id_2,relationship_type)
);
CREATE TABLE IF NOT EXISTS analysis_runs (
 analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
 analysis_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 status TEXT NOT NULL,
 summary TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analysis_conflicts (
 conflict_id INTEGER PRIMARY KEY AUTOINCREMENT,
 analysis_id INTEGER NOT NULL REFERENCES analysis_runs(analysis_id) ON DELETE CASCADE,
 relationship_id INTEGER REFERENCES event_relationships(relationship_id) ON DELETE SET NULL,
 event_id_1 INTEGER REFERENCES evidence_events(event_id) ON DELETE SET NULL,
 event_id_2 INTEGER REFERENCES evidence_events(event_id) ON DELETE SET NULL,
 explanation TEXT NOT NULL
);
