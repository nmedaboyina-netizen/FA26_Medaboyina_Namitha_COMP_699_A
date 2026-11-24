import json
from flask import Blueprint, render_template, redirect, url_for, abort, Response
from src.services.event_service import list_events
from src.services.constraint_service import get_relationships
from src.algorithms.conflict_detection import analyze
from src.algorithms.alternative_timelines import generate_alternatives
from src.services.report_service import save_analysis, get_analysis, get_analysis_snapshot

bp = Blueprint("analysis", __name__, url_prefix="/analysis")


@bp.post("/run")
def run():
    events = [dict(row) for row in list_events()]
    relationships = [dict(row) for row in get_relationships()]
    conflicts = analyze(events, relationships)
    status = "INCONSISTENT" if conflicts else "CONSISTENT"
    summary = f"Checked {len(events)} evidence events and {len(relationships)} BEFORE relationships."
    if not events:
        summary += " Add evidence events before relying on an analysis result."
    alternatives = generate_alternatives(events, relationships) if not conflicts else []
    analysis_id = save_analysis(status, summary, conflicts, events, relationships, alternatives)
    return redirect(url_for("analysis.results", analysis_id=analysis_id))


@bp.get("/<int:analysis_id>")
def results(analysis_id):
    run_record, conflicts = get_analysis(analysis_id)
    if run_record is None:
        abort(404)
    snapshot = get_analysis_snapshot(run_record)
    events = snapshot["events"]
    relationships = snapshot["relationships"]
    alternatives = snapshot["alternatives"]
    names = {int(event["event_id"]): event["description"] for event in events}
    return render_template(
        "analysis/results.html", run=run_record, conflicts=conflicts,
        alternatives=alternatives, event_names=names, events=events,
        relationships=relationships
    )


@bp.get("/<int:analysis_id>/export")
def export(analysis_id):
    run_record, conflicts = get_analysis(analysis_id)
    if run_record is None:
        abort(404)
    snapshot = get_analysis_snapshot(run_record)
    payload = {
        "analysis_id": analysis_id,
        "analysis_time": run_record["analysis_time"],
        "status": run_record["status"],
        "summary": run_record["summary"],
        "events": snapshot["events"],
        "relationships": snapshot["relationships"],
        "conflicts": [dict(conflict) for conflict in conflicts],
        "candidate_alternative_orders": snapshot["alternatives"],
        "note": "Computational analysis only; this output is not a conclusion about guilt or evidence reliability."
    }
    return Response(
        json.dumps(payload, indent=2, default=str),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename=timeline_analysis_{analysis_id}.json"}
    )
