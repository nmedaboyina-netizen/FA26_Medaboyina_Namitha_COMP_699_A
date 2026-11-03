import csv
from src.models.evidence_event import validate_event
from src.services.event_service import create_event
REQUIRED={"description","start_time","end_time","location","duration_minutes"}
def import_csv(upload):
    reader=csv.DictReader(line.decode("utf-8-sig") for line in upload.stream)
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("CSV requires columns: "+", ".join(sorted(REQUIRED)))
    rows=list(reader); validated=[]
    for number,row in enumerate(rows,start=2):
        event,errors=validate_event(row)
        if errors: raise ValueError(f"CSV row {number}: "+" ".join(errors))
        validated.append(event)
    for event in validated: create_event(event)
    return len(validated)
