# Forensic Timeline Consistency Analyzer — Proof of Concept

A small local Flask + SQLite prototype. It stores synthetic evidence events and flags overlapping time ranges recorded at different locations. It uses Python, HTML, CSS, and no custom JavaScript.

## Run on Windows / VS Code

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. Select **Load synthetic demo data** to load a small example.

## Prototype rule and limitations

The prototype flags two events if their time intervals overlap and their recorded location strings differ. This is a deliberately simple screening rule. It does not account for travel time, uncertain timestamps, location aliases, event dependencies, or legitimate explanations. It must not be treated as a forensic conclusion. The full project needs richer constraint definitions, graph relationships, robust alternative timeline solving, import/export, and tests.

The database file `forensic_poc.db` is created automatically in the project directory. Only use synthetic or authorized data.
