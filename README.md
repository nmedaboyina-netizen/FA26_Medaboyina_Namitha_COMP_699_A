
# Forensic Timeline Consistency and Evidence Constraint Analyzer

## 1. Project Overview

The Forensic Timeline Consistency and Evidence Constraint Analyzer is a
Python-based web application designed to organize forensic evidence events
and check whether their timelines are consistent with defined constraints.

Forensic investigators may need to compare evidence records containing
timestamps, estimated time ranges, locations, durations, and relationships
between events. Checking these details manually can make contradictions
difficult to identify.

This project aims to provide a system that organizes evidence events,
checks temporal and other supported constraints, identifies potential
conflicts, and generates alternative timelines when valid solutions exist.

The application will be developed using Python, Flask, HTML, CSS, and SQLite.
It will run locally on a standard computer and will not require specialized
hardware or private forensic case databases.

## 2. Project Objectives

The main objectives are to:

- Organize evidence events in a structured format.
- Allow users to add, view, edit, and delete evidence events.
- Store timestamps, estimated time ranges, locations, and durations.
- Represent relationships between evidence events as a graph.
- Define and validate constraints between events.
- Detect potential inconsistencies in incident timelines.
- Identify the evidence events and constraints involved in detected conflicts.
- Generate alternative timelines that satisfy supported constraints.
- Display timeline information and analysis results.
- Import and export evidence data using CSV and JSON files.
- Test the algorithms using synthetic forensic datasets.
- Demonstrate data processing using selected public NIBRS records.

The system focuses on computational timeline consistency. It will not
determine guilt, innocence, or the reliability of real-world evidence.

## 3. Intended Users

### Forensic Investigators

Investigators will enter evidence events, define relationships, run timeline
analysis, review conflicts, and examine alternative timelines.

### Forensic Analysts

Analysts will examine constraint violations, review affected event records,
and compare the alternative timelines produced by the system.

### System Administrator

If administrative functionality is implemented, the administrator will
manage application configuration and support database maintenance.

### External Data Sources

Public datasets, including selected National Incident-Based Reporting System
(NIBRS) records, may be transformed into the event format used by the
application.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language and analysis logic |
| Flask | Web application framework |
| HTML | Page structure and forms |
| CSS | Page styling and layout |
| Jinja | Dynamic HTML template rendering |
| SQLite | Local relational database |
| NetworkX | Graph representation of event relationships |
| python-constraint | Constraint-solving support |
| Pandas | Data cleaning and transformation |
| NumPy | Numerical calculations where required |
| datetime | Timestamp and time-range handling |
| CSV | Tabular data import and export |
| JSON | Structured data import and export |
| pytest | Automated testing |
| Visual Studio Code | Development environment |

The application will use HTML forms and server-rendered pages. No custom
JavaScript is planned. Timeline visualizations must use static or
server-generated output when necessary to preserve this requirement.

Machine learning is optional. The primary analysis will use explicit rules,
graph algorithms, and constraint-solving techniques.

## 5. System Architecture

The application is organized into the following layers.

### Presentation Layer

Provides HTML pages and CSS styling for evidence management, constraint
management, timeline analysis, and reports.

### Flask Application Layer

Receives user requests, validates submitted forms, calls application
services, and returns rendered HTML pages.

### Evidence Management Layer

Handles evidence-event creation, retrieval, editing, deletion, and validation.

### Constraint Analysis Layer

Represents event relationships and evaluates temporal, location, duration,
and ordering constraints supported by the application.

### Data Processing Layer

Imports, validates, transforms, and exports CSV and JSON records. It may also
transform selected public NIBRS records into the application's event format.

### Visualization and Reporting Layer

Displays analysis summaries, potential conflicts, affected event identifiers,
and available alternative timelines.

### Database Layer

Uses SQLite to store evidence events, relationships, constraints, and
analysis records.

## 6. Planned Source Tree

The following structure describes the intended organization of the project.
Files and features should be marked as implemented only after they have been
created and tested.

```text
forensic_timeline_analyzer/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── instance/
│   └── forensic_timeline.db
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── db.py
│   │   └── schema.sql
│   ├── models/
│   │   └── evidence_event.py
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── events.py
│   │   ├── constraints.py
│   │   ├── analysis.py
│   │   └── datasets.py
│   ├── services/
│   │   ├── event_service.py
│   │   ├── graph_service.py
│   │   ├── constraint_service.py
│   │   ├── conflict_service.py
│   │   ├── timeline_service.py
│   │   └── report_service.py
│   ├── algorithms/
│   │   ├── temporal_checks.py
│   │   ├── location_checks.py
│   │   ├── conflict_detection.py
│   │   └── alternative_timelines.py
│   ├── data_processing/
│   │   ├── csv_importer.py
│   │   ├── json_importer.py
│   │   └── nibrs_transformer.py
│   └── ml/
│       └── event_classifier.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── events/
│   │   ├── list.html
│   │   ├── add.html
│   │   └── edit.html
│   ├── constraints/
│   │   └── list.html
│   ├── analysis/
│   │   ├── results.html
│   │   ├── conflicts.html
│   │   └── alternatives.html
│   └── reports/
│       └── detail.html
├── static/
│   └── css/
│       └── style.css
├── datasets/
│   ├── synthetic/
│   └── samples/
└── tests/
    ├── test_events.py
    ├── test_constraints.py
    ├── test_conflicts.py
    └── test_alternative_timelines.py
```

## 7. Source Code Responsibilities

| File or directory | Responsibility |
|---|---|
| `app.py` | Starts and configures the Flask application |
| `config.py` | Stores application settings |
| `requirements.txt` | Lists Python dependencies |
| `src/database/` | Database connections and schema |
| `src/models/` | Evidence-event data structures |
| `src/routes/` | Flask routes and request handling |
| `src/services/` | Application business logic |
| `src/algorithms/` | Constraint checking and timeline algorithms |
| `src/data_processing/` | Data import, transformation, and export |
| `src/ml/` | Optional event-description classification |
| `templates/` | HTML templates |
| `static/css/` | CSS stylesheets |
| `datasets/synthetic/` | Synthetic test scenarios |
| `datasets/samples/` | Small sample import files |
| `tests/` | Automated tests |

## 8. Functional Requirements

The planned system will support the following functions:

1. Add, view, edit, and delete evidence events.
2. Record event descriptions, timestamps, estimated time ranges, locations,
   and durations.
3. Define relationships between evidence events.
4. Construct incident timelines from recorded events.
5. Check event ordering and supported temporal constraints.
6. Detect potential conflicts and identify affected event records.
7. Generate alternative timelines when valid solutions exist.
8. Display timelines and analysis results.
9. Import evidence records from CSV and JSON files.
10. Export evidence records and analysis results.
11. Load synthetic datasets for testing.
12. Transform selected NIBRS records into the application's event format.
13. Display analysis reports and explanations of violated constraints.
14. Validate inputs before saving or analyzing records.
15. Keep original evidence records separate from generated alternatives.

These functions describe the intended system. Their implementation status
must be confirmed during development.

## 9. Database Design

SQLite will provide persistent local storage.

The planned database entities include:

### Evidence_Event

Stores event identifiers, descriptions, start and end times, locations,
durations, source types, and creation timestamps.

### Event_Relationship

Stores relationships between two evidence events, including relationship
types and descriptions.

### Constraint

Stores supported constraint types, affected event identifiers, operators,
expected values, and descriptions.

### Analysis_Run

Stores the time and status of an analysis and a summary of its results.

### Analysis_Conflict

Stores detected conflicts, related analysis identifiers, violated
constraints, affected event identifiers, and explanations.

### Alternative_Timeline

Stores proposed alternative event assignments and their validation status.

Primary keys and foreign keys will be used to maintain database integrity.
Python validation will check event time ranges and other input requirements.

The SQLite database file may be created when the application initializes.
The schema script should be maintained so that the database can be recreated.

## 10. Installation and Setup

### Prerequisites

Install the following software:

- Python 3.11 or another version supported by the selected dependencies.
- Visual Studio Code.
- Python extension for Visual Studio Code.
- Git, if the project is managed in a Git repository.

Verify Python installation:

```powershell
python --version
```

### Step 1: Open the Project

Open the `forensic_timeline_analyzer` folder in Visual Studio Code.

Open a terminal and confirm that the terminal is in the project root.

### Step 2: Create a Virtual Environment

On Windows PowerShell:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If activation is blocked by the terminal's execution policy, use an
approved activation method for your environment.

### Step 3: Install Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

An initial `requirements.txt` may contain:

```text
Flask
pandas
numpy
networkx
python-constraint2
pytest
```

Pin package versions after the application has been installed and tested.
If a library import differs from its installed package name, follow the
selected library's documentation and update the dependency list accordingly.

SQLite is included with standard Python installations. The optional machine
learning extension may require `scikit-learn` if that feature is implemented.

## 11. Running the Application

From the project root, run:

```powershell
python app.py
```

If the application starts successfully, Flask will display a local address
in the terminal. Open that address in your browser. It is commonly:

```text
http://127.0.0.1:5000/
```

The exact startup command depends on the implemented application entry point.
The command should be tested and kept consistent with the actual code.

If the application fails to start:

1. Confirm that the virtual environment is activated.
2. Confirm that the dependencies were installed.
3. Check that `app.py` exists in the project root.
4. Check the terminal error message.
5. Confirm that the Flask application and its registered routes are implemented.
6. Confirm that the database initialization code and schema file are available.

## 12. Database Initialization

The database helper should connect to:

```text
instance/forensic_timeline.db
```

The schema should be initialized from:

```text
src/database/schema.sql
```

The database initialization code should:

1. Create the instance directory when needed.
2. Open a SQLite connection.
3. Enable foreign-key enforcement.
4. Create the required tables if they do not exist.
5. Close database connections safely.

The database should not contain private or sensitive forensic case records.
Use synthetic records for development and testing.

## 13. Example Analysis Scenario

A synthetic scenario can be used to demonstrate the central analysis
functionality.

Suppose the dataset contains two events:

- Event E001: A person is recorded at Location A from 10:00 to 10:20.
- Event E002: A person is recorded at Location B from 10:10 to 10:30.

If the system has a supported rule that the same person cannot be at both
locations at the same time, it may flag the overlapping time ranges for
review.

This example does not automatically establish that either record is false.
Additional rules, uncertainty, travel time, and other information may affect
the analysis.

The example is a proposed test scenario, not a claim that the full analysis
functionality has already been implemented.

## 14. Testing

Automated tests will be written using pytest.

Run the test suite from the project root:

```powershell
pytest
```

The tests should cover:

- Valid evidence-event creation.
- Missing required fields.
- Invalid timestamps and time ranges.
- Supported event-ordering constraints.
- Known conflicting event scenarios.
- Cases where no conflict should be reported.
- Alternative timelines that satisfy the supported constraints.
- CSV and JSON import validation.

Tests should use controlled synthetic data with known expected outcomes.

Only report tests as passed after running them and confirming their results.

## 15. Data Sources

### Synthetic Forensic Datasets

Synthetic data will provide controlled examples of event times, locations,
relationships, uncertain time ranges, and known contradictions.

These datasets will help verify whether the algorithms produce the expected
results.

### National Incident-Based Reporting System (NIBRS)

Selected publicly available NIBRS records may be used to demonstrate
incident-data processing.

The data will need to be examined and transformed into the event format
supported by the application. Not every NIBRS field will necessarily provide
the detailed event timestamps or relationships needed for constraint analysis.

Synthetic records will supplement scenarios that the public data cannot
represent.

## 16. Development Plan

### Week 1: Implementation Foundation

- Organize the initial source tree.
- Create the application configuration and dependency files.
- Establish the Flask execution foundation.
- Add initial database setup code and schema.
- Implement an initial executable operation or algorithm.
- Document setup and verify the current implementation.

### Week 2: Core Application Foundation

- Complete Flask route registration and shared templates.
- Complete SQLite initialization and database operations.
- Implement evidence-event creation, listing, editing, and deletion.
- Add input validation for timestamps and time ranges.
- Implement initial event-ordering constraints.
- Add preliminary conflict reporting.
- Create synthetic test cases and automated tests.

### Later Development

- Expand temporal and location constraint checking.
- Integrate NetworkX graph operations.
- Improve conflict explanations.
- Implement alternative timeline generation.
- Add CSV and JSON import/export.
- Process selected NIBRS records.
- Improve timeline visualization and reports.
- Consider an optional event-description classifier.
- Test the application against larger synthetic datasets.

## 17. Known Limitations

The system's conclusions depend on the quality of the recorded data and the
constraints implemented in the application.

Potential limitations include:

- Uncertain or incomplete timestamps.
- Missing or ambiguous location information.
- Incomplete event relationships.
- Complex constraints that may require substantial search.
- Large numbers of possible alternative timelines.
- Differences between public dataset fields and the application's event model.

Alternative timelines represent solutions to the encoded constraints.
They are not proof that a particular sequence actually occurred.

The application will not determine guilt, innocence, or evidence reliability.







