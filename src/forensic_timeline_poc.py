import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

TIME_FORMAT = "%Y-%m-%d %H:%M"

st.set_page_config(
    page_title="Forensic Timeline Analyzer",
    page_icon="🔎",
    layout="wide",
)

# ----------------------------- Data models ----------------------------- #

@dataclass
class EvidenceEvent:
    event_id: str
    description: str
    earliest_time: str
    latest_time: str
    location: str
    duration_minutes: int = 0

    def get_time_domain(self, step_minutes=5):
        if step_minutes <= 0:
            raise ValueError("Time resolution must be greater than zero.")

        earliest = datetime.strptime(self.earliest_time, TIME_FORMAT)
        latest = datetime.strptime(self.latest_time, TIME_FORMAT)

        if earliest > latest:
            raise ValueError(f"Invalid time range for {self.event_id}.")
        if self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative.")

        times = []
        current = earliest
        while current <= latest:
            times.append(current)
            current += timedelta(minutes=step_minutes)
        return times


@dataclass
class EvidenceConstraint:
    constraint_id: str
    event_a: str
    event_b: str
    constraint_type: str
    minimum_gap: int = 0
    maximum_gap: Optional[int] = None
    description: str = ""

    def is_satisfied(self, time_a, time_b):
        difference = (time_b - time_a).total_seconds() / 60
        if difference < self.minimum_gap:
            return False
        if self.maximum_gap is not None and difference > self.maximum_gap:
            return False
        return True


class TimelineAnalyzer:
    def __init__(self, events, constraints, step_minutes=5):
        self.events = {event.event_id: event for event in events}
        self.constraints = constraints
        self.step_minutes = step_minutes
        self.validate_data()

    def validate_data(self):
        if not self.events:
            raise ValueError("At least one event is required.")
        if self.step_minutes <= 0:
            raise ValueError("Time resolution must be greater than zero.")

        event_ids = [event.event_id for event in self.events.values()]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("Event IDs must be unique.")

        constraint_ids = [item.constraint_id for item in self.constraints]
        if len(constraint_ids) != len(set(constraint_ids)):
            raise ValueError("Constraint IDs must be unique.")

        for event in self.events.values():
            if not event.event_id.strip():
                raise ValueError("Event ID cannot be empty.")
            if event.duration_minutes < 0:
                raise ValueError(f"Duration cannot be negative for {event.event_id}.")
            earliest = datetime.strptime(event.earliest_time, TIME_FORMAT)
            latest = datetime.strptime(event.latest_time, TIME_FORMAT)
            if earliest > latest:
                raise ValueError(f"Earliest time must not be after latest time for {event.event_id}.")

        for constraint in self.constraints:
            if constraint.event_a not in self.events or constraint.event_b not in self.events:
                raise ValueError(f"{constraint.constraint_id} references a missing event.")
            if constraint.event_a == constraint.event_b:
                raise ValueError("A constraint must reference two different events.")
            if constraint.minimum_gap < 0:
                raise ValueError("Minimum gap cannot be negative.")
            if constraint.maximum_gap is not None and constraint.maximum_gap < constraint.minimum_gap:
                raise ValueError(f"Invalid gap range in {constraint.constraint_id}.")
            if not constraint.constraint_type.strip():
                raise ValueError("Constraint type cannot be empty.")

    def get_domains(self):
        return {
            event_id: event.get_time_domain(self.step_minutes)
            for event_id, event in self.events.items()
        }

    def solve(self, constraints=None, max_solutions=5):
        constraints = self.constraints if constraints is None else constraints
        domains = self.get_domains()
        event_order = sorted(domains, key=lambda event_id: len(domains[event_id]))
        solutions = []
        assignment = {}

        def is_consistent(event_id, candidate_time):
            for constraint in constraints:
                if event_id == constraint.event_a and constraint.event_b in assignment:
                    if not constraint.is_satisfied(candidate_time, assignment[constraint.event_b]):
                        return False
                elif event_id == constraint.event_b and constraint.event_a in assignment:
                    if not constraint.is_satisfied(assignment[constraint.event_a], candidate_time):
                        return False
            return True

        def backtrack(index):
            if len(solutions) >= max_solutions:
                return
            if index == len(event_order):
                solutions.append(assignment.copy())
                return
            event_id = event_order[index]
            for candidate_time in domains[event_id]:
                if is_consistent(event_id, candidate_time):
                    assignment[event_id] = candidate_time
                    backtrack(index + 1)
                    del assignment[event_id]
                    if len(solutions) >= max_solutions:
                        return

        backtrack(0)
        return solutions

    def find_conflicting_constraints(self):
        conflict_group = list(self.constraints)
        for constraint in list(conflict_group):
            remaining = [
                item for item in conflict_group
                if item.constraint_id != constraint.constraint_id
            ]
            if not self.solve(constraints=remaining, max_solutions=1):
                conflict_group = remaining
        return conflict_group

    def get_event_table(self):
        return pd.DataFrame([
            {
                "Event ID": event.event_id,
                "Description": event.description,
                "Earliest Time": event.earliest_time,
                "Latest Time": event.latest_time,
                "Location": event.location,
                "Duration (minutes)": event.duration_minutes,
            }
            for event in self.events.values()
        ])

    def get_constraint_table(self):
        return pd.DataFrame([
            {
                "Constraint ID": item.constraint_id,
                "Event A": item.event_a,
                "Event B": item.event_b,
                "Type": item.constraint_type,
                "Minimum Gap (minutes)": item.minimum_gap,
                "Maximum Gap (minutes)": item.maximum_gap if item.maximum_gap is not None else "No limit",
                "Rule": item.description,
            }
            for item in self.constraints
        ])


# ----------------------------- Sample data ----------------------------- #

def create_scenario(scenario_type):
    if scenario_type == "Inconsistent timeline":
        events = [
            EvidenceEvent("E01", "Person observed at Location A", "2026-10-14 10:00", "2026-10-14 10:10", "Location A"),
            EvidenceEvent("E02", "Person observed at Location B", "2026-10-14 10:05", "2026-10-14 10:15", "Location B"),
        ]
    else:
        events = [
            EvidenceEvent("E01", "Person observed at Location A", "2026-10-14 10:00", "2026-10-14 10:10", "Location A"),
            EvidenceEvent("E02", "Person observed at Location B", "2026-10-14 10:35", "2026-10-14 10:45", "Location B"),
        ]

    constraints = [
        EvidenceConstraint(
            "C01", "E01", "E02", "TRAVEL_TIME",
            minimum_gap=30,
            description="At least 30 minutes are required to travel from Location A to Location B.",
        )
    ]
    return events, constraints


def event_to_dict(event):
    return {
        "event_id": event.event_id,
        "description": event.description,
        "earliest_time": event.earliest_time,
        "latest_time": event.latest_time,
        "location": event.location,
        "duration_minutes": event.duration_minutes,
    }


def constraint_to_dict(item):
    return {
        "constraint_id": item.constraint_id,
        "event_a": item.event_a,
        "event_b": item.event_b,
        "constraint_type": item.constraint_type,
        "minimum_gap": item.minimum_gap,
        "maximum_gap": item.maximum_gap,
        "description": item.description,
    }


def parse_events_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    required = {"event_id", "description", "earliest_time", "latest_time", "location"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Events CSV is missing columns: " + ", ".join(sorted(missing)))

    imported = []
    for _, row in df.iterrows():
        duration_value = row.get("duration_minutes", 0)
        duration = 0 if pd.isna(duration_value) else int(duration_value)
        imported.append(EvidenceEvent(
            str(row["event_id"]).strip(),
            "" if pd.isna(row["description"]) else str(row["description"]),
            str(row["earliest_time"]).strip(),
            str(row["latest_time"]).strip(),
            "" if pd.isna(row["location"]) else str(row["location"]),
            duration,
        ))
    return imported


# ----------------------------- Session state ----------------------------- #

if "custom_events" not in st.session_state:
    st.session_state.custom_events = []
if "custom_constraints" not in st.session_state:
    st.session_state.custom_constraints = []
if "last_solutions" not in st.session_state:
    st.session_state.last_solutions = []
if "last_status" not in st.session_state:
    st.session_state.last_status = None
if "imported_events" not in st.session_state:
    st.session_state.imported_events = []


# ----------------------------- Sidebar controls ----------------------------- #

st.title("Forensic Timeline Consistency and Evidence Constraint Analyzer")
st.write(
    "Use this proof of concept to organize evidence events, check time constraints, "
    "identify possible conflicts, and view alternative timelines."
)
st.info(
    "This demonstration uses synthetic or user-entered information. It does not determine "
    "guilt, innocence, authenticity, or evidence reliability. Keep original evidence unchanged."
)

scenario_type = st.sidebar.selectbox(
    "Select a test scenario",
    ["Inconsistent timeline", "Consistent timeline"],
)
step_minutes = st.sidebar.selectbox("Time resolution", [1, 5, 10, 15], index=1)
max_solutions = st.sidebar.slider("Maximum alternative timelines", 1, 10, 5)

st.sidebar.divider()
st.sidebar.header("Add Evidence Event")
with st.sidebar.form("add_event_form", clear_on_submit=True):
    event_id = st.text_input("Event ID", "E03")
    description = st.text_input("Event description", "Person observed at another location")
    earliest_time = st.text_input("Earliest time (YYYY-MM-DD HH:MM)", "2026-10-14 11:00")
    latest_time = st.text_input("Latest time (YYYY-MM-DD HH:MM)", "2026-10-14 11:10")
    location = st.text_input("Location", "Location C")
    duration = st.number_input("Duration in minutes", min_value=0, value=0, step=1)
    add_event = st.form_submit_button("Add Event")

base_events, base_constraints = create_scenario(scenario_type)
existing_ids = {event.event_id for event in base_events + st.session_state.custom_events + st.session_state.imported_events}

if add_event:
    try:
        datetime.strptime(earliest_time.strip(), TIME_FORMAT)
        datetime.strptime(latest_time.strip(), TIME_FORMAT)
        if not event_id.strip():
            st.sidebar.error("Event ID cannot be empty.")
        elif event_id.strip() in existing_ids:
            st.sidebar.error("That Event ID already exists in the current scenario.")
        elif datetime.strptime(earliest_time.strip(), TIME_FORMAT) > datetime.strptime(latest_time.strip(), TIME_FORMAT):
            st.sidebar.error("Earliest time must be before or equal to latest time.")
        else:
            st.session_state.custom_events.append(EvidenceEvent(
                event_id.strip(), description.strip(), earliest_time.strip(),
                latest_time.strip(), location.strip(), int(duration),
            ))
            st.session_state.last_status = None
            st.sidebar.success("Evidence event added.")
            st.rerun()
    except ValueError as error:
        st.sidebar.error(f"Please check the event details: {error}")

st.sidebar.divider()
st.sidebar.header("Import Evidence Events")
st.sidebar.caption("CSV columns required: event_id, description, earliest_time, latest_time, location. duration_minutes is optional.")
uploaded_events = st.sidebar.file_uploader("Upload events CSV", type=["csv"], key="events_csv")
if st.sidebar.button("Import CSV events", disabled=uploaded_events is None):
    try:
        imported = parse_events_csv(uploaded_events)
        current_ids = {event.event_id for event in base_events + st.session_state.custom_events + st.session_state.imported_events}
        new_ids = [event.event_id for event in imported]
        if len(new_ids) != len(set(new_ids)):
            raise ValueError("The CSV contains duplicate event IDs.")
        if any(not item_id for item_id in new_ids):
            raise ValueError("The CSV contains an empty event ID.")
        duplicates = current_ids.intersection(new_ids)
        if duplicates:
            raise ValueError("These event IDs already exist: " + ", ".join(sorted(duplicates)))
        # Validate imported event times and ranges before storing them.
        for event in imported:
            datetime.strptime(event.earliest_time, TIME_FORMAT)
            datetime.strptime(event.latest_time, TIME_FORMAT)
            if datetime.strptime(event.earliest_time, TIME_FORMAT) > datetime.strptime(event.latest_time, TIME_FORMAT):
                raise ValueError(f"Invalid time range for {event.event_id}.")
            if event.duration_minutes < 0:
                raise ValueError(f"Negative duration for {event.event_id}.")
        st.session_state.imported_events.extend(imported)
        st.session_state.last_status = None
        st.sidebar.success(f"Imported {len(imported)} event(s).")
        st.rerun()
    except Exception as error:
        st.sidebar.error(f"Could not import CSV: {error}")

events = base_events + st.session_state.custom_events + st.session_state.imported_events
constraints = base_constraints + st.session_state.custom_constraints

st.sidebar.divider()
st.sidebar.header("Add Time Constraint")
event_ids = [event.event_id for event in events]
if len(event_ids) >= 2:
    with st.sidebar.form("add_constraint_form", clear_on_submit=True):
        constraint_id = st.text_input("Constraint ID", "C02")
        event_a = st.selectbox("Event A (time before Event B)", event_ids)
        event_b = st.selectbox("Event B (time after Event A)", event_ids, index=1 if len(event_ids) > 1 else 0)
        constraint_type = st.selectbox("Constraint type", ["TRAVEL_TIME", "SEQUENCE", "TIME_GAP"])
        minimum_gap = st.number_input("Minimum gap in minutes", min_value=0, value=10, step=1)
        maximum_gap_input = st.number_input("Maximum gap in minutes (0 means no limit)", min_value=0, value=0, step=1)
        rule_description = st.text_input("Constraint explanation", "Event B must occur within the allowed time gap after Event A.")
        add_constraint = st.form_submit_button("Add Constraint")
    if add_constraint:
        if event_a == event_b:
            st.sidebar.error("Select two different events.")
        elif not constraint_id.strip():
            st.sidebar.error("Constraint ID cannot be empty.")
        elif any(item.constraint_id == constraint_id.strip() for item in constraints):
            st.sidebar.error("This Constraint ID already exists.")
        else:
            st.session_state.custom_constraints.append(EvidenceConstraint(
                constraint_id.strip(), event_a, event_b, constraint_type,
                int(minimum_gap), int(maximum_gap_input) if maximum_gap_input > 0 else None,
                rule_description.strip(),
            ))
            st.session_state.last_status = None
            st.rerun()
else:
    st.sidebar.caption("Add at least two events to create a constraint.")

with st.sidebar.expander("Session tools"):
    if st.button("Clear user-added data", type="secondary"):
        st.session_state.custom_events = []
        st.session_state.custom_constraints = []
        st.session_state.imported_events = []
        st.session_state.last_solutions = []
        st.session_state.last_status = None
        st.rerun()
    st.caption("This clears only events and constraints added or imported during this session. Sample scenario data stays available.")

# ----------------------------- Main analysis ----------------------------- #

try:
    analyzer = TimelineAnalyzer(events, constraints, step_minutes=step_minutes)

    event_tab, constraint_tab, analysis_tab, timeline_tab, export_tab = st.tabs([
        "Evidence Events", "Constraints", "Consistency Analysis", "Timeline Visualization", "Export & Reports"
    ])

    with event_tab:
        st.subheader("Evidence Event Register")
        event_df = analyzer.get_event_table()
        search_text = st.text_input("Search events", placeholder="Search ID, description, or location")
        if search_text:
            mask = event_df.astype(str).apply(
                lambda column: column.str.contains(search_text, case=False, na=False)
            ).any(axis=1)
            event_df = event_df[mask]
        location_options = ["All locations"] + sorted(event_df["Location"].dropna().astype(str).unique().tolist())
        selected_location = st.selectbox("Filter by location", location_options)
        if selected_location != "All locations":
            event_df = event_df[event_df["Location"].astype(str) == selected_location]
        st.dataframe(event_df, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(event_df)} event(s) after filters.")

        all_user_events = st.session_state.custom_events + st.session_state.imported_events
        user_event_ids = [item.event_id for item in all_user_events]
        if user_event_ids:
            st.markdown("#### Manage user-added events")
            edit_or_remove_id = st.selectbox("Choose an event to edit or remove", user_event_ids, key="manage_event_id")
            selected_event = next(item for item in all_user_events if item.event_id == edit_or_remove_id)
            with st.form("edit_event_form"):
                edit_description = st.text_input("Description", selected_event.description)
                edit_earliest = st.text_input("Earliest time", selected_event.earliest_time)
                edit_latest = st.text_input("Latest time", selected_event.latest_time)
                edit_location = st.text_input("Location", selected_event.location)
                edit_duration = st.number_input("Duration (minutes)", min_value=0, value=int(selected_event.duration_minutes), step=1)
                save_edit = st.form_submit_button("Save event changes")
            col1, col2 = st.columns(2)
            if save_edit:
                try:
                    datetime.strptime(edit_earliest.strip(), TIME_FORMAT)
                    datetime.strptime(edit_latest.strip(), TIME_FORMAT)
                    if datetime.strptime(edit_earliest.strip(), TIME_FORMAT) > datetime.strptime(edit_latest.strip(), TIME_FORMAT):
                        raise ValueError("Earliest time must be before or equal to latest time.")
                    updated = EvidenceEvent(
                        selected_event.event_id, edit_description.strip(), edit_earliest.strip(),
                        edit_latest.strip(), edit_location.strip(), int(edit_duration),
                    )
                    for collection in (st.session_state.custom_events, st.session_state.imported_events):
                        for index, item in enumerate(collection):
                            if item.event_id == edit_or_remove_id:
                                collection[index] = updated
                    st.session_state.last_status = None
                    st.success("Event updated.")
                    st.rerun()
                except ValueError as error:
                    st.error(f"Could not update event: {error}")
            with col1:
                if st.button("Remove selected event"):
                    st.session_state.custom_events = [item for item in st.session_state.custom_events if item.event_id != edit_or_remove_id]
                    st.session_state.imported_events = [item for item in st.session_state.imported_events if item.event_id != edit_or_remove_id]
                    st.session_state.custom_constraints = [
                        item for item in st.session_state.custom_constraints
                        if item.event_a != edit_or_remove_id and item.event_b != edit_or_remove_id
                    ]
                    st.session_state.last_solutions = []
                    st.session_state.last_status = None
                    st.rerun()

    with constraint_tab:
        st.subheader("Evidence Constraint Register")
        if constraints:
            st.dataframe(analyzer.get_constraint_table(), use_container_width=True, hide_index=True)
            user_constraint_ids = [item.constraint_id for item in st.session_state.custom_constraints]
            if user_constraint_ids:
                remove_constraint_id = st.selectbox("Remove a user-added constraint", user_constraint_ids)
                if st.button("Remove selected constraint"):
                    st.session_state.custom_constraints = [
                        item for item in st.session_state.custom_constraints if item.constraint_id != remove_constraint_id
                    ]
                    st.session_state.last_status = None
                    st.rerun()
        else:
            st.write("No constraints have been added.")

    with analysis_tab:
        st.subheader("Timeline Consistency Results")
        st.caption("The solver checks candidate event times at the selected time resolution. A consistent result means at least one assignment satisfies the configured constraints.")
        if st.button("Run Consistency Analysis", type="primary"):
            with st.spinner("Checking possible timelines..."):
                solutions = analyzer.solve(max_solutions=max_solutions)
            st.session_state.last_solutions = [
                {
                    "Alternative": number,
                    "Event ID": event_id,
                    "Assigned Time": assigned_time.strftime(TIME_FORMAT),
                    "Location": analyzer.events[event_id].location,
                    "Description": analyzer.events[event_id].description,
                }
                for number, solution in enumerate(solutions, start=1)
                for event_id, assigned_time in solution.items()
            ]
            st.session_state.last_status = "CONSISTENT" if solutions else "INCONSISTENT"
            st.session_state.last_conflicts = []
            if not solutions:
                conflicts = analyzer.find_conflicting_constraints()
                st.session_state.last_conflicts = [
                    {
                        "Constraint ID": item.constraint_id,
                        "Event A": item.event_a,
                        "Event B": item.event_b,
                        "Rule": item.description,
                        "Event A Time Range": f"{analyzer.events[item.event_a].earliest_time} to {analyzer.events[item.event_a].latest_time}",
                        "Event B Time Range": f"{analyzer.events[item.event_b].earliest_time} to {analyzer.events[item.event_b].latest_time}",
                    }
                    for item in conflicts
                ]

        if st.session_state.last_status == "CONSISTENT":
            st.success("Status: CONSISTENT")
            st.write("At least one timeline satisfies all active time constraints.")
            solution_df = pd.DataFrame(st.session_state.last_solutions)
            st.dataframe(solution_df, use_container_width=True, hide_index=True)
            alternatives = solution_df["Alternative"].nunique() if not solution_df.empty else 0
            if alternatives == max_solutions:
                st.warning("The display limit was reached. Additional valid timelines may exist.")
        elif st.session_state.last_status == "INCONSISTENT":
            st.error("Status: INCONSISTENT")
            st.write("No timeline satisfies all active time constraints.")
            conflicts_df = pd.DataFrame(st.session_state.get("last_conflicts", []))
            if not conflicts_df.empty:
                st.subheader("Reduced Conflicting Constraint Group")
                st.dataframe(conflicts_df, use_container_width=True, hide_index=True)
                st.warning("This is one reduced conflicting group, not necessarily the only possible explanation.")
            else:
                st.info("Check the event time ranges and input data.")
        else:
            st.info("Select **Run Consistency Analysis** to calculate results.")

    with timeline_tab:
        st.subheader("Interactive Evidence Timeline")
        timeline_rows = []
        for event in events:
            timeline_rows.append({
                "Event": event.event_id,
                "Description": event.description,
                "Location": event.location or "(not specified)",
                "Start": datetime.strptime(event.earliest_time, TIME_FORMAT),
                "Finish": datetime.strptime(event.latest_time, TIME_FORMAT),
                "Duration (minutes)": event.duration_minutes,
            })
        timeline_df = pd.DataFrame(timeline_rows)
        if not timeline_df.empty:
            timeline_locations = ["All locations"] + sorted(timeline_df["Location"].unique().tolist())
            timeline_location = st.selectbox("Timeline location filter", timeline_locations)
            if timeline_location != "All locations":
                timeline_df = timeline_df[timeline_df["Location"] == timeline_location]
            fig = px.timeline(
                timeline_df, x_start="Start", x_end="Finish", y="Event", color="Location",
                hover_data=["Description", "Location", "Duration (minutes)"],
                title="Allowed Time Ranges for Evidence Events",
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(xaxis_title="Date and Time", yaxis_title="Evidence Event", legend_title="Location")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Bars show allowed time ranges, not confirmed event times or proof that an event occurred.")

        if st.session_state.last_status == "CONSISTENT" and st.session_state.last_solutions:
            st.markdown("#### Selected alternative timeline")
            solution_df = pd.DataFrame(st.session_state.last_solutions)
            alternative_numbers = sorted(solution_df["Alternative"].unique().tolist())
            selected_alt = st.selectbox("Alternative number", alternative_numbers)
            alt_df = solution_df[solution_df["Alternative"] == selected_alt].copy()
            alt_df["Assigned Time"] = pd.to_datetime(alt_df["Assigned Time"], format=TIME_FORMAT)
            alt_fig = px.scatter(
                alt_df, x="Assigned Time", y="Event ID", color="Location",
                hover_data=["Description"], title=f"Candidate Assigned Times — Alternative {selected_alt}",
            )
            alt_fig.update_yaxes(autorange="reversed")
            st.plotly_chart(alt_fig, use_container_width=True)

    with export_tab:
        st.subheader("Export Evidence Data and Analysis")
        event_export = pd.DataFrame([event_to_dict(item) for item in events])
        constraint_export = pd.DataFrame([constraint_to_dict(item) for item in constraints])
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download evidence events (CSV)",
                data=event_export.to_csv(index=False).encode("utf-8"),
                file_name="forensic_evidence_events.csv",
                mime="text/csv",
            )
        with c2:
            st.download_button(
                "Download constraints (CSV)",
                data=constraint_export.to_csv(index=False).encode("utf-8"),
                file_name="forensic_evidence_constraints.csv",
                mime="text/csv",
            )

        report = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "scenario": scenario_type,
            "time_resolution_minutes": step_minutes,
            "status": st.session_state.last_status,
            "events": [event_to_dict(item) for item in events],
            "constraints": [constraint_to_dict(item) for item in constraints],
            "candidate_timelines": st.session_state.last_solutions,
            "conflicting_constraints": st.session_state.get("last_conflicts", []),
            "notice": "Computational demonstration only. This report does not determine guilt, innocence, authenticity, or evidence reliability.",
        }
        st.download_button(
            "Download analysis report (JSON)",
            data=json.dumps(report, indent=2, default=str),
            file_name="forensic_timeline_report.json",
            mime="application/json",
        )
        st.caption("The report includes the current scenario, events, constraints, and the latest analysis result if analysis has been run.")

except (ValueError, KeyError) as error:
    st.error(f"Unable to analyze the current data: {error}")

st.divider()
st.caption(
    "Technical proof of concept | Synthetic or user-entered data | "
    "Original evidence is not modified."
)
