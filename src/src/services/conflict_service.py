from src.algorithms.conflict_detection import analyze
from src.services.event_service import list_events
from src.services.constraint_service import get_relationships

def run_conflict_analysis():
    """Run the currently supported temporal and graph consistency checks."""
    return analyze(list_events(), get_relationships())
