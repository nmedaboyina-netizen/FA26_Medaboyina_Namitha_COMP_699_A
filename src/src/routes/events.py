from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from src.models.evidence_event import validate_event
from src.services import event_service
bp=Blueprint("events",__name__,url_prefix="/events")
@bp.get("/")
def list_page():
    return render_template("events/list.html",events=event_service.list_events())
@bp.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        event,errors=validate_event(request.form)
        if errors:
            for error in errors: flash(error,"error")
        else:
            event_service.create_event(event); flash("Evidence event saved.","success")
            return redirect(url_for("events.list_page"))
    return render_template("events/form.html",event=None,page_title="Add Evidence Event")
@bp.route("/<int:event_id>/edit",methods=["GET","POST"])
def edit(event_id):
    old=event_service.get_event(event_id)
    if old is None: abort(404)
    if request.method=="POST":
        event,errors=validate_event(request.form)
        if errors:
            for error in errors: flash(error,"error")
        else:
            event_service.update_event(event_id,event); flash("Evidence event updated.","success")
            return redirect(url_for("events.list_page"))
    else: event=dict(old)
    return render_template("events/form.html",event=event,page_title="Edit Evidence Event")
@bp.post("/<int:event_id>/delete")
def delete(event_id):
    if event_service.get_event(event_id) is None: abort(404)
    event_service.delete_event(event_id); flash("Evidence event deleted.","success")
    return redirect(url_for("events.list_page"))
