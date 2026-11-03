import json
from src.models.evidence_event import validate_event
from src.services.event_service import create_event
def import_json(upload):
    try: rows=json.load(upload)
    except (ValueError,UnicodeDecodeError) as exc: raise ValueError("Invalid JSON file.") from exc
    if not isinstance(rows,list): raise ValueError("JSON must contain a list of event objects.")
    validated=[]
    for i,row in enumerate(rows,start=1):
        event,errors=validate_event(row)
        if errors: raise ValueError(f"JSON record {i}: "+" ".join(errors))
        validated.append(event)
    for event in validated: create_event(event)
    return len(validated)
