# Forensic Timeline Consistency and Evidence Constraint Analyzer

## Project Overview

The Forensic Timeline Consistency and Evidence Constraint Analyzer is a Python-based application designed to organize forensic evidence events, check timeline consistency, identify conflicting constraints, and generate alternative timelines that satisfy the available evidence.

The application provides a Streamlit web interface where users can view evidence events, examine time constraints, run consistency analysis, and visualize event time ranges. It helps users understand why certain events may not fit together within the specified timeline.

## Features

- Add and manage forensic evidence events.
- Define event time ranges, locations, descriptions, and durations.
- Create time-based constraints between evidence events.
- Check whether all events can satisfy the defined constraints.
- Identify conflicting constraints when a timeline is inconsistent.
- Generate alternative timelines when valid solutions exist.
- Visualize evidence time ranges using interactive Plotly charts.
- Export evidence event data to CSV.
- Demonstrate the system using synthetic forensic scenarios.

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Dataclasses
- Datetime

## Installation

1. Install Python on your computer.
2. Clone this repository or download the project files.
3. Open a terminal in the project directory.
4. Install the required libraries using the following command:

```bash
pip install streamlit pandas plotly
```

## Running the Application

Run the following command from the project directory:

```bash
streamlit run app.py
```

Replace `app.py` with the name of the Python file containing the Streamlit application if your file has a different name.

Streamlit will open the application in your web browser.

## How to Use

1. Select a consistent or inconsistent timeline scenario from the sidebar.
2. Review the available evidence events and their time ranges.
3. Add custom evidence events using the sidebar form.
4. Define time constraints between events when needed.
5. Run the consistency analysis to check whether a valid timeline exists.
6. Review alternative timelines or the conflicting constraint group.
7. Open the timeline visualization tab to compare evidence time ranges.
8. Download the evidence event register as a CSV file.

## Data and Demonstration

The current proof of concept uses synthetic forensic evidence events to demonstrate timeline consistency checking and conflict identification. The sample scenarios include both consistent and inconsistent timelines.

The project is designed to support future integration with publicly available datasets, including the National Incident-Based Reporting System (NIBRS), after the relevant records are transformed into the application's event-and-constraint format.

## Project Limitations

- The current proof of concept uses synthetic sample data.
- Time constraints are based on user-defined rules and time ranges.
- The application does not establish whether evidence is authentic or reliable.
- The application does not determine guilt or innocence.
- Alternative timelines represent possible solutions under the defined constraints, not confirmed accounts of an incident.

## Future Improvements

- Integrate publicly available NIBRS data.
- Add evidence editing and persistent database storage.
- Represent evidence relationships using NetworkX.
- Improve constraint solving for larger datasets.
- Add more detailed conflict explanations and alternative timeline comparisons.
- Support importing and exporting complete event and constraint datasets.

## Author

Developed as a software development course project to demonstrate constraint-based reasoning, timeline analysis, and interactive visualization using Python.
