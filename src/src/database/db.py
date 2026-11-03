import sqlite3
from pathlib import Path
from flask import current_app, g
from config import DATABASE_PATH

def get_db():
    if "db" not in g:
        path = current_app.config.get("DATABASE", str(DATABASE_PATH))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    db = get_db()
    db.executescript(schema)
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
