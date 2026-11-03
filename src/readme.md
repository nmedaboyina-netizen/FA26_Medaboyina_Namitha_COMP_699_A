# Forensic Timeline Consistency and Evidence Constraint Analyzer

A local Flask application for managing evidence events, recording event-order
constraints, checking timeline consistency, reporting conflicts, and generating
candidate alternative event orders.

## Stack
Python, Flask, HTML, CSS, Jinja, SQLite, NetworkX, Pandas, pytest.
No custom JavaScript is used.

## Week 2 implemented scope
- Create, view, edit, and delete evidence events.
- Validate descriptions, timestamps, time ranges, locations, and durations.
- Define `BEFORE` relationships between events.
- Check whether each `BEFORE` rule is satisfied.
- Detect cycles in the relationship graph.
- Store analysis runs and conflict explanations.
- Generate candidate topological event orders for small acyclic graphs.
- Import CSV/JSON events and export event records.
- Keep generated orders separate from original evidence records.

NIBRS transformation and machine-learning classification are not implemented
in this milestone. The `BEFORE` rule means the first event must finish before
the second event starts. Alternative generation is limited to nine events.

## Windows setup (VS Code terminal)
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000/.

## Tests
```powershell
pytest -q
```

The SQLite database is created in `instance/` automatically. Do not commit
real or sensitive forensic case records.

