from src.services.event_service import list_events

def get_chronological_timeline():
    """Return stored events in chronological start-time order."""
    return list_events()
