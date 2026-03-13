from app.schemas.chronos_schema import (
    ScheduleRequest,
    Session,
    Venue,
    FixedSlot
)

from app.agents.chronos_agent import chronos_agent, remove_session
from app.scheduler_engine.schedule_builder import build_schedule
from app.scheduler_engine.conflict_detector import detect_conflicts
from app.scheduler_engine.resolution_engine import resolve_conflicts
from app.scheduler_engine.constraint_parser import parse_constraints
from app.scheduler_engine.constraint_optimizer import apply_constraints
from app.scheduler_engine.what_if_engine import simulate_change


# ------------------------------------------------
# UTILITY PRINT FUNCTIONS
# ------------------------------------------------

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_schedule(schedule):

    for s in schedule:
        print(
            f"Day {s['day']} | {s['start_time']} - {s['end_time']} | "
            f"{s['venue']} | {s['title']} ({s.get('speaker')})"
        )


# ------------------------------------------------
# TEST DATA
# ------------------------------------------------

venues = [
    Venue(name="Hall A", capacity=100),
    Venue(name="Hall B", capacity=80)
]

sessions = [
    Session(id="S1", title="AI Ethics", speaker="Dr Sharma", duration_minutes=60),
    Session(id="S2", title="Robotics", speaker="Dr Mehta", duration_minutes=60),
    Session(id="S3", title="Deep Learning", speaker="Dr Gupta", duration_minutes=60),
]

fixed_slots = [
    FixedSlot(
        id="F1",
        title="Opening Ceremony",
        venue="Hall A",
        day=1,
        start_time="09:00",
        end_time="10:00"
    )
]


# ------------------------------------------------
# TEST 1 — SCHEDULE BUILDER
# ------------------------------------------------

print_section("TEST 1 — Schedule Builder")

schedule = build_schedule(
    sessions=sessions,
    venues=venues,
    fixed_slots=fixed_slots,
    days=1
)

print_schedule(schedule)


# ------------------------------------------------
# TEST 2 — FORCE A CONFLICT
# ------------------------------------------------

print_section("TEST 2 — Conflict Detection")

# manually create conflict
schedule.append({
    "id": "S4",
    "title": "Conflict Talk",
    "speaker": "Dr Sharma",
    "venue": "Hall A",
    "day": 1,
    "start_time": "10:00",
    "end_time": "11:00",
    "status": "scheduled"
})

conflicts = detect_conflicts(schedule)

print("Detected Conflicts:")
for c in conflicts:
    print(c)


# ------------------------------------------------
# TEST 3 — RESOLUTION ENGINE
# ------------------------------------------------

print_section("TEST 3 — Conflict Resolution")

venue_names = [v.name for v in venues]

schedule, resolutions = resolve_conflicts(
    schedule,
    conflicts,
    venue_names,
    days=1
)

print_schedule(schedule)

print("\nResolutions:")
for r in resolutions:
    print(r)


# ------------------------------------------------
# TEST 4 — CONSTRAINT PARSER
# ------------------------------------------------

print_section("TEST 4 — Constraint Parser")

constraints = [
    "Dr Sharma only available after 14:00"
]

parsed = parse_constraints(constraints)

print("Parsed Constraints:")
print(parsed)


# ------------------------------------------------
# TEST 5 — CONSTRAINT OPTIMIZER
# ------------------------------------------------

print_section("TEST 5 — Constraint Optimizer")

schedule, warnings = apply_constraints(schedule, parsed)

print_schedule(schedule)

print("\nWarnings:")
print(warnings)


# ------------------------------------------------
# TEST 6 — WHAT IF SIMULATION
# ------------------------------------------------

print_section("TEST 6 — What‑If Simulation")

result = simulate_change(schedule, "S1", "11:00")

print("Moved Session:")
print(result["moved_session"])

print("\nSimulated Schedule:")
print_schedule(result["simulated_schedule"])

print("\nConflicts from simulation:")
print(result["conflicts_found"])


# ------------------------------------------------
# TEST 7 — REMOVE SESSION
# ------------------------------------------------

print_section("TEST 7 — Remove Session")

remove_result = remove_session(schedule, "S2")

print("Removed:", remove_result["removed_session"])

print("\nUpdated Schedule:")
print_schedule(remove_result["updated_schedule"])


# ------------------------------------------------
# TEST 8 — FULL CHRONOS AGENT
# ------------------------------------------------

print_section("TEST 8 — Full Chronos Agent Pipeline")

request = ScheduleRequest(
    event_name="Demo AI Conference",
    days=1,
    venues=venues,
    sessions=sessions,
    constraints=[
        "Dr Sharma only available after 13:00"
    ],
    fixed_slots=fixed_slots
)

result = chronos_agent(request)

print("\nFinal Timeline:")
for s in result.timeline:
    print(
        f"Day {s.day} | {s.start_time}-{s.end_time} | "
        f"{s.venue} | {s.title}"
    )

print("\nConflicts Found:")
print(result.conflicts_found)

print("\nResolutions:")
print(result.conflicts_resolved)

print("\nWarnings:")
print(result.warnings)

print("\nReasoning:")
print(result.reasoning)