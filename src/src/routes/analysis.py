from flask import Blueprint,render_template,redirect,url_for,abort
from src.services.event_service import list_events
from src.services.constraint_service import get_relationships
from src.algorithms.conflict_detection import analyze
from src.algorithms.alternative_timelines import generate_alternatives
from src.services.report_service import save_analysis,get_analysis
bp=Blueprint("analysis",__name__,url_prefix="/analysis")
@bp.post("/run")
def run():
    events=list_events(); rels=get_relationships(); conflicts=analyze(events,rels)
    status="INCONSISTENT" if conflicts else "CONSISTENT"
    summary=f"Checked {len(events)} events and {len(rels)} ordering relationships."
    aid=save_analysis(status,summary,conflicts)
    return redirect(url_for("analysis.results",analysis_id=aid))
@bp.get("/<int:analysis_id>")
def results(analysis_id):
    run,conflicts=get_analysis(analysis_id)
    if run is None: abort(404)
    alternatives=generate_alternatives(list_events(),get_relationships())
    return render_template("analysis/results.html",run=run,conflicts=conflicts,alternatives=alternatives)
