from datetime import datetime


def validate_event(description, start_time, end_time, location):
    if not all([description.strip(), start_time.strip(), end_time.strip(), location.strip()]):
        return "All fields are required."
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except ValueError:
        return "Use a valid date and time in YYYY-MM-DD HH:MM format."
    if end < start:
        return "End time cannot be earlier than start time."
    return None


def analyze_events(events):
    """Flag overlapping event intervals recorded at different locations.

    This is a simple demonstrator rule, not a forensic conclusion.
    """
    conflicts = []
    parsed = []
    for event in events:
        try:
            start = datetime.fromisoformat(event["start_time"])
            end = datetime.fromisoformat(event["end_time"])
        except (ValueError, TypeError, KeyError):
            continue
        parsed.append((event, start, end))
    for i in range(len(parsed)):
        e1, s1, f1 = parsed[i]
        for j in range(i + 1, len(parsed)):
            e2, s2, f2 = parsed[j]
            overlaps = max(s1, s2) < min(f1, f2)
            if overlaps and e1["location"].strip().casefold() != e2["location"].strip().casefold():
                conflicts.append({
                    "event_id_1": e1["event_id"],
                    "event_id_2": e2["event_id"],
                    "description_1": e1["description"],
                    "description_2": e2["description"],
                    "location_1": e1["location"],
                    "location_2": e2["location"],
                    "explanation": "The event time ranges overlap, but the recorded locations differ. This needs review under the system's assumptions."
                })
    return conflicts
