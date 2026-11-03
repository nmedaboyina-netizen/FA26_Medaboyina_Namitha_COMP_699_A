import csv,io,json
from flask import Blueprint,render_template,request,redirect,url_for,flash,Response
from src.data_processing.csv_importer import import_csv
from src.data_processing.json_importer import import_json
from src.services.event_service import list_events
bp=Blueprint("datasets",__name__,url_prefix="/data")
@bp.get("/")
def index(): return render_template("datasets.html")
@bp.post("/import")
def import_data():
    upload=request.files.get("file")
    if not upload or not upload.filename:
        flash("Choose a CSV or JSON file.","error"); return redirect(url_for("datasets.index"))
    try:
        name=upload.filename.lower()
        count=import_csv(upload) if name.endswith(".csv") else import_json(upload) if name.endswith(".json") else None
        if count is None: raise ValueError("Only CSV and JSON files are supported.")
        flash(f"Imported {count} evidence events.","success")
    except ValueError as exc: flash(str(exc),"error")
    return redirect(url_for("datasets.index"))
@bp.get("/export/<kind>")
def export_data(kind):
    events=[dict(x) for x in list_events()]
    if kind=="json":
        return Response(json.dumps(events,indent=2),mimetype="application/json",
          headers={"Content-Disposition":"attachment; filename=evidence_events.json"})
    if kind=="csv":
        output=io.StringIO(); fields=["event_id","description","start_time","end_time","location","duration_minutes","source_type","created_at"]
        writer=csv.DictWriter(output,fieldnames=fields); writer.writeheader(); writer.writerows(events)
        return Response(output.getvalue(),mimetype="text/csv",
          headers={"Content-Disposition":"attachment; filename=evidence_events.csv"})
    flash("Unsupported format.","error"); return redirect(url_for("datasets.index"))
