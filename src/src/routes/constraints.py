from flask import Blueprint,render_template,request,redirect,url_for,flash
from src.services.event_service import list_events
from src.services.constraint_service import list_relationships,add_before
bp=Blueprint("constraints",__name__,url_prefix="/constraints")
@bp.get("/")
def index():
    return render_template("constraints/list.html",events=list_events(),relationships=list_relationships())
@bp.post("/add-before")
def add_before_route():
    try:
        add_before(int(request.form["event_a"]),int(request.form["event_b"]),request.form.get("description",""))
        flash("BEFORE relationship saved.","success")
    except (ValueError,KeyError) as exc: flash(str(exc),"error")
    return redirect(url_for("constraints.index"))
