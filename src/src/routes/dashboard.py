from flask import Blueprint,render_template
from src.services.event_service import list_events
from src.services.constraint_service import list_relationships
bp=Blueprint("dashboard",__name__)
@bp.get("/")
def index():
    return render_template("dashboard.html",events=list_events(),relationships=list_relationships())
