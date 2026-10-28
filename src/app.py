from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "forensic_poc.db"
app = Flask(__name__)
app.secret_key = "development-only-change-before-deployment"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS evidence_event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT NOT NULL
        )""")


from analysis_core import validate_event, analyze_events


@app.route("/", methods=["GET"])
def index():
    with get_db() as conn:
        events = conn.execute("SELECT * FROM evidence_event ORDER BY start_time, event_id").fetchall()
    event_dicts = [dict(row) for row in events]
    conflicts = analyze_events(event_dicts)
    return render_template("index.html", events=event_dicts, conflicts=conflicts)


@app.route("/events/add", methods=["POST"])
def add_event():
    description = request.form.get("description", "")
    start_time = request.form.get("start_time", "")
    end_time = request.form.get("end_time", "")
    location = request.form.get("location", "")
    error = validate_event(description, start_time, end_time, location)
    if error:
        flash(error, "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute(
            "INSERT INTO evidence_event (description, start_time, end_time, location) VALUES (?, ?, ?, ?)",
            (description.strip(), start_time.strip(), end_time.strip(), location.strip())
        )
    flash("Evidence event saved.", "success")
    return redirect(url_for("index"))


@app.route("/demo/reset", methods=["POST"])
def reset_demo():
    """Reset to a small, clearly synthetic demonstration scenario."""
    with get_db() as conn:
        conn.execute("DELETE FROM evidence_event")
        conn.execute("""INSERT INTO evidence_event (description, start_time, end_time, location) VALUES
            (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)""", (
            "Synthetic: camera observation", "2026-10-01 10:00", "2026-10-01 10:30", "Warehouse A",
            "Synthetic: reported phone activity", "2026-10-01 10:15", "2026-10-01 10:25", "Downtown Office",
            "Synthetic: witness interview", "2026-10-01 11:00", "2026-10-01 11:20", "Station B"
        ))
    flash("Synthetic demo data loaded.", "success")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
