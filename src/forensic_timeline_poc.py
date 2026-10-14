
# I am using Streamlit to display my forensic timeline analyzer
# directly in a web interface instead of showing results only in the terminal.

import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

# I am keeping the same date and time format throughout my POC.
TIME_FORMAT = "%Y-%m-%d %H:%M"

st.set_page_config(
    page_title="Forensic Timeline Analyzer",
    page_icon="",
    layout="wide"
)


# I am defining each evidence event with its time range,
# location, description, and duration.
@dataclass
class EvidenceEvent:
    event_id: str
    description: str
    earliest_time: str
    latest_time: str
    location: str
    duration_minutes: int = 0

    def get_time_domain(self, step_minutes=5):
        earliest = datetime.strptime(self.earliest_time, TIME_FORMAT)
        latest = datetime.strptime(self.latest_time, TIME_FORMAT)

        if earliest > latest:
            raise ValueError(f"Invalid time range for {self.event_id}")

        if self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative.")

        times = []
        current = earliest

        while current <= latest:
            times.append(current)
            current += timedelta(minutes=step_minutes)

        return times


# I am using constraints to define the allowed time gap
# between two evidence events.
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

        if (
            self.maximum_gap is not None
            and difference > self.maximum_gap
        ):
            return False

        return True


# I am building the constraint solver using backtracking.
# It checks possible event times and rejects invalid combinations.
class TimelineAnalyzer:

    def __init__(self, events, constraints, step_minutes=5):
        self.events = {event.event_id: event for event in events}
        self.constraints = constraints
        self.step_minutes = step_minutes
        self.validate_data()

    def validate_data(self):
        if not self.events:
            raise ValueError("At least one event is required.")

        constraint_ids = [
            constraint.constraint_id
            for constraint in self.constraints
        ]

        if len(constraint_ids) != len(set(constraint_ids)):
            raise ValueError("Constraint IDs must be unique.")

        for constraint in self.constraints:
            if (
                constraint.event_a not in self.events
                or constraint.event_b not in self.events
            ):
                raise ValueError(
                    f"{constraint.constraint_id} references a missing event."
                )

            if constraint.event_a == constraint.event_b:
                raise ValueError(
                    "A constraint must reference two different events."
                )

            if constraint.minimum_gap < 0:
                raise ValueError("Minimum gap cannot be negative.")

            if (
                constraint.maximum_gap is not None
                and constraint.maximum_gap < constraint.minimum_gap
            ):
                raise ValueError(
                    f"Invalid gap range in {constraint.constraint_id}."
                )

            if not constraint.constraint_type.strip():
                raise ValueError("Constraint type cannot be empty.")

    def get_domains(self):
        return {
            event_id: event.get_time_domain(self.step_minutes)
            for event_id, event in self.events.items()
        }

    def solve(self, constraints=None, max_solutions=5):
        if constraints is None:
            constraints = self.constraints

        domains = self.get_domains()

        # I am checking events with fewer possible times first
        # to reduce the search space.
        event_order = sorted(
            domains,
            key=lambda event_id: len(domains[event_id])
        )

        solutions = []
        assignment = {}

        def is_consistent(event_id, candidate_time):
            for constraint in constraints:

                if event_id == constraint.event_a:
                    other_id = constraint.event_b

                    if other_id in assignment:
                        if not constraint.is_satisfied(
                            candidate_time,
                            assignment[other_id]
                        ):
                            return False

                elif event_id == constraint.event_b:
                    other_id = constraint.event_a

                    if other_id in assignment:
                        if not constraint.is_satisfied(
                            assignment[other_id],
                            candidate_time
                        ):
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

    # I am identifying a conflicting group of constraints
    # when no valid timeline can satisfy all the rules.
    def find_conflicting_constraints(self):
        conflict_group = list(self.constraints)

        for constraint in list(conflict_group):
            remaining = [
                item for item in conflict_group
                if item.constraint_id != constraint.constraint_id
            ]

            if not self.solve(
                constraints=remaining,
                max_solutions=1
            ):
                conflict_group = remaining

        return conflict_group

    # I am converting the analysis results into a table
    # that Streamlit can display on the screen.
    def get_event_table(self):
        return pd.DataFrame([
            {
                "Event ID": event.event_id,
                "Description": event.description,
                "Earliest Time": event.earliest_time,
                "Latest Time": event.latest_time,
                "Location": event.location,
                "Duration (minutes)": event.duration_minutes
            }
            for event in self.events.values()
        ])

    def get_constraint_table(self):
        return pd.DataFrame([
            {
                "Constraint ID": constraint.constraint_id,
                "Event A": constraint.event_a,
                "Event B": constraint.event_b,
                "Type": constraint.constraint_type,
                "Minimum Gap (minutes)": constraint.minimum_gap,
                "Maximum Gap (minutes)": (
                    constraint.maximum_gap
                    if constraint.maximum_gap is not None
                    else "No limit"
                ),
                "Rule": constraint.description
            }
            for constraint in self.constraints
        ])


# I am providing synthetic data so I can demonstrate
# both consistent and inconsistent timeline scenarios.
def create_scenario(scenario_type):
    if scenario_type == "Inconsistent timeline":
        events = [
            EvidenceEvent(
                "E01",
                "Person observed at Location A",
                "2026-10-14 10:00",
                "2026-10-14 10:10",
                "Location A"
            ),
            EvidenceEvent(
                "E02",
                "Person observed at Location B",
                "2026-10-14 10:05",
                "2026-10-14 10:15",
                "Location B"
            )
        ]
    else:
        events = [
            EvidenceEvent(
                "E01",
                "Person observed at Location A",
                "2026-10-14 10:00",
                "2026-10-14 10:10",
                "Location A"
            ),
            EvidenceEvent(
                "E02",
                "Person observed at Location B",
                "2026-10-14 10:35",
                "2026-10-14 10:45",
                "Location B"
            )
        ]

    constraints = [
        EvidenceConstraint(
            "C01",
            "E01",
            "E02",
            "TRAVEL_TIME",
            minimum_gap=30,
            description=(
                "At least 30 minutes are required to travel "
                "from Location A to Location B."
            )
        )
    ]

    return events, constraints


# I am setting up the main Streamlit page.
st.title("Forensic Timeline Consistency and Evidence Constraint Analyzer")

st.write(
    "I developed this proof of concept to organize synthetic evidence "
    "events, check timeline constraints, identify conflicts, and "
    "display alternative timelines."
)

st.info(
    "This is a computational demonstration using synthetic evidence. "
    "It does not determine guilt, innocence, or evidence reliability."
)

# I am allowing the user to select a scenario to analyze.
scenario_type = st.sidebar.selectbox(
    "Select a test scenario",
    ["Inconsistent timeline", "Consistent timeline"]
)

step_minutes = st.sidebar.selectbox(
    "Time resolution",
    [1, 5, 10, 15],
    index=1
)

max_solutions = st.sidebar.slider(
    "Maximum alternative timelines",
    min_value=1,
    max_value=10,
    value=5
)

# I am allowing users to enter their own evidence events.
st.sidebar.header("Add Evidence Event")

with st.sidebar.form("add_event_form"):
    event_id = st.text_input("Event ID", "E03")
    description = st.text_input(
        "Event description",
        "Person observed at another location"
    )
    earliest_time = st.text_input(
        "Earliest time",
        "2026-10-14 11:00"
    )
    latest_time = st.text_input(
        "Latest time",
        "2026-10-14 11:10"
    )
    location = st.text_input("Location", "Location C")
    duration = st.number_input(
        "Duration in minutes",
        min_value=0,
        value=0
    )

    add_event = st.form_submit_button("Add Event")

# I am storing additional user-created events during the session.
if "custom_events" not in st.session_state:
    st.session_state.custom_events = []

if "custom_constraints" not in st.session_state:
    st.session_state.custom_constraints = []

if add_event:
    try:
        datetime.strptime(earliest_time, TIME_FORMAT)
        datetime.strptime(latest_time, TIME_FORMAT)

        if not event_id.strip():
            st.sidebar.error("Event ID cannot be empty.")
        elif any(
            event.event_id == event_id.strip()
            for event in st.session_state.custom_events
        ):
            st.sidebar.error("This custom event ID already exists.")
        else:
            # I am keeping the original sample events unchanged
            # and adding user-created events separately.
            st.session_state.custom_events.append(
                EvidenceEvent(
                    event_id.strip(),
                    description,
                    earliest_time,
                    latest_time,
                    location,
                    int(duration)
                )
            )
            st.sidebar.success("Evidence event added.")

    except ValueError as error:
        st.sidebar.error(f"Please check the event time: {error}")

# I am preparing the selected scenario and adding custom events.
events, constraints = create_scenario(scenario_type)
events.extend(st.session_state.custom_events)
constraints.extend(st.session_state.custom_constraints)

# I am allowing users to create relationships between events.
st.sidebar.header("Add Time Constraint")

event_ids = [event.event_id for event in events]

if len(event_ids) >= 2:
    with st.sidebar.form("add_constraint_form"):
        constraint_id = st.text_input("Constraint ID", "C02")
        event_a = st.selectbox("Earlier event", event_ids)
        event_b = st.selectbox(
            "Later event",
            event_ids,
            index=1 if len(event_ids) > 1 else 0
        )
        constraint_type = st.selectbox(
            "Constraint type",
            ["TRAVEL_TIME", "SEQUENCE", "TIME_GAP"]
        )
        minimum_gap = st.number_input(
            "Minimum gap in minutes",
            min_value=0,
            value=10
        )
        maximum_gap_input = st.number_input(
            "Maximum gap in minutes (0 means no limit)",
            min_value=0,
            value=0
        )
        rule_description = st.text_input(
            "Constraint explanation",
            "The second event must occur after the first event."
        )

        add_constraint = st.form_submit_button("Add Constraint")

    if add_constraint:
        if event_a == event_b:
            st.sidebar.error("Select two different events.")
        elif not constraint_id.strip():
            st.sidebar.error("Constraint ID cannot be empty.")
        elif any(
            item.constraint_id == constraint_id.strip()
            for item in constraints
        ):
            st.sidebar.error("This constraint ID already exists.")
        else:
            st.session_state.custom_constraints.append(
                EvidenceConstraint(
                    constraint_id.strip(),
                    event_a,
                    event_b,
                    constraint_type,
                    int(minimum_gap),
                    (
                        int(maximum_gap_input)
                        if maximum_gap_input > 0
                        else None
                    ),
                    rule_description
                )
            )
            st.rerun()

# I am analyzing the events and constraints and displaying
# the results directly inside the Streamlit interface.
try:
    analyzer = TimelineAnalyzer(
        events,
        constraints,
        step_minutes=step_minutes
    )

    tab_events, tab_constraints, tab_analysis, tab_timeline = st.tabs(
        [
            "Evidence Events",
            "Constraints",
            "Consistency Analysis",
            "Timeline Visualization"
        ]
    )

    with tab_events:
        st.subheader("Evidence Event Register")
        st.dataframe(
            analyzer.get_event_table(),
            use_container_width=True,
            hide_index=True
        )

        # I am showing a form for removing custom events.
        custom_ids = [
            event.event_id
            for event in st.session_state.custom_events
        ]

        if custom_ids:
            event_to_remove = st.selectbox(
                "Select a custom event to remove",
                custom_ids
            )

            if st.button("Remove Selected Event"):
                st.session_state.custom_events = [
                    event
                    for event in st.session_state.custom_events
                    if event.event_id != event_to_remove
                ]

                # I am also removing constraints that reference
                # the deleted event so the data remains valid.
                st.session_state.custom_constraints = [
                    constraint
                    for constraint in st.session_state.custom_constraints
                    if (
                        constraint.event_a != event_to_remove
                        and constraint.event_b != event_to_remove
                    )
                ]
                st.rerun()

    with tab_constraints:
        st.subheader("Evidence Constraint Register")
        if constraints:
            st.dataframe(
                analyzer.get_constraint_table(),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No constraints have been added.")

    # I am running the solver only when the user requests analysis.
    with tab_analysis:
        st.subheader("Timeline Consistency Results")

        if st.button("Run Consistency Analysis", type="primary"):
            solutions = analyzer.solve(
                max_solutions=max_solutions
            )

            if solutions:
                st.success("Status: CONSISTENT")

                st.write(
                    "At least one timeline satisfies all active "
                    "time constraints."
                )

                solution_rows = []

                for number, solution in enumerate(solutions, start=1):
                    for event_id, assigned_time in solution.items():
                        event = analyzer.events[event_id]

                        solution_rows.append({
                            "Alternative": number,
                            "Event ID": event_id,
                            "Assigned Time": assigned_time,
                            "Location": event.location,
                            "Description": event.description
                        })

                solution_df = pd.DataFrame(solution_rows)

                st.subheader("Alternative Timelines")
                st.dataframe(
                    solution_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.session_state.last_solutions = solution_rows

                if len(solutions) == max_solutions:
                    st.warning(
                        "The display limit was reached. Additional "
                        "valid timelines may exist."
                    )

            else:
                st.error("Status: INCONSISTENT")

                st.write(
                    "No timeline satisfies all active time constraints."
                )

                conflicts = analyzer.find_conflicting_constraints()

                if conflicts:
                    st.subheader("Conflicting Constraint Group")

                    conflict_rows = []

                    for constraint in conflicts:
                        event_a = analyzer.events[constraint.event_a]
                        event_b = analyzer.events[constraint.event_b]

                        conflict_rows.append({
                            "Constraint ID": constraint.constraint_id,
                            "Event A": constraint.event_a,
                            "Event B": constraint.event_b,
                            "Rule": constraint.description,
                            "Event A Time Range": (
                                f"{event_a.earliest_time} to "
                                f"{event_a.latest_time}"
                            ),
                            "Event B Time Range": (
                                f"{event_b.earliest_time} to "
                                f"{event_b.latest_time}"
                            )
                        })

                    st.dataframe(
                        pd.DataFrame(conflict_rows),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.warning(
                        "This is one reduced conflicting constraint group, "
                        "not necessarily the only possible explanation."
                    )

                else:
                    st.info(
                        "Check the event time ranges and input data."
                    )

    with tab_timeline:
        st.subheader("Interactive Evidence Timeline")

        # I am displaying each event's allowed time range
        # so users can compare evidence windows visually.
        timeline_rows = []

        for event in events:
            timeline_rows.append({
                "Event": event.event_id,
                "Description": event.description,
                "Location": event.location,
                "Start": datetime.strptime(
                    event.earliest_time,
                    TIME_FORMAT
                ),
                "Finish": datetime.strptime(
                    event.latest_time,
                    TIME_FORMAT
                )
            })

        timeline_df = pd.DataFrame(timeline_rows)

        if not timeline_df.empty:
            fig = px.timeline(
                timeline_df,
                x_start="Start",
                x_end="Finish",
                y="Event",
                color="Location",
                hover_data=["Description", "Location"],
                title="Allowed Time Ranges for Evidence Events"
            )

            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                xaxis_title="Date and Time",
                yaxis_title="Evidence Event",
                legend_title="Location"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                "The bars show the allowed time ranges, not confirmed "
                "event times or proof that an event occurred."
            )

except (ValueError, KeyError) as error:
    st.error(f"Unable to analyze the current data: {error}")

# I am providing a download option so the evidence event
# register can be saved as a CSV file.
st.divider()
st.subheader("Export Evidence Data")

try:
    export_events = pd.DataFrame([
        {
            "event_id": event.event_id,
            "description": event.description,
            "earliest_time": event.earliest_time,
            "latest_time": event.latest_time,
            "location": event.location,
            "duration_minutes": event.duration_minutes
        }
        for event in events
    ])

    st.download_button(
        label="Download Evidence Events as CSV",
        data=export_events.to_csv(index=False),
        file_name="forensic_evidence_events.csv",
        mime="text/csv"
    )

except (ValueError, KeyError) as error:
    st.error(f"Unable to prepare the CSV export: {error}")

st.caption(
    "Technical proof of concept | Synthetic forensic data | "
    "Original evidence is not modified."
)
