from datetime import datetime

def validate_event(data):
    errors = []
    description = (data.get("description") or "").strip()
    location = (data.get("location") or "").strip()
    if not description:
        errors.append("Event description is required.")
    if not location:
        errors.append("Location is required.")
    start_text = (data.get("start_time") or "").strip()
    end_text = (data.get("end_time") or "").strip()
    try:
        start = datetime.fromisoformat(start_text)
        end = datetime.fromisoformat(end_text)
        if end < start:
            errors.append("End time must be the same as or later than start time.")
    except ValueError:
        errors.append("Enter valid start and end date/time values.")
    try:
        duration = float(data.get("duration_minutes", "0"))
        if duration < 0:
            errors.append("Duration cannot be negative.")
    except (TypeError, ValueError):
        duration = 0
        errors.append("Duration must be a number.")
    return {
        "description": description, "start_time": start_text, "end_time": end_text,
        "location": location, "duration_minutes": duration,
        "source_type": (data.get("source_type") or "Other").strip() or "Other"
    }, errors
