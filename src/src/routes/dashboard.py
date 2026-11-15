from flask import Blueprint, render_template
from src.services.event_service import list_events
from src.services.constraint_service import list_relationships
from src.database.db import get_db

bp = Blueprint("dashboard", __name__)

@bp.get("/")
def index():
    events = list_events()
    relationships = list_relationships()
    latest = get_db().execute("SELECT * FROM analysis_runs ORDER BY analysis_id DESC LIMIT 1").fetchone()
    return render_template("dashboard.html", events=events, relationships=relationships, latest=latest)
