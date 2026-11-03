from datetime import datetime

def check_before(event_a,event_b):
    # BEFORE means event A must finish at or before event B starts.
    return datetime.fromisoformat(event_a["end_time"]) <= datetime.fromisoformat(event_b["start_time"])
