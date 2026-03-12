from app.schemas.chronos_schema import ScheduleRequest, ScheduleResult

from app.scheduler_engine.schedule_optimizer import build_schedule
from app.scheduler_engine.conflict_detector import detect_conflicts
from app.scheduler_engine.resolution_engine import resolve_conflicts
from app.scheduler_engine.constraint_parser import parse_constraints
from app.scheduler_engine.constraint_optimizer import apply_constraints
from app.scheduler_engine.what_if_engine import simulate_change

from app.services.llm_service import get_llm


def chronos_agent(request: ScheduleRequest):

    # STEP 1 — Parse natural language constraints
    structured_constraints = []

    if request.constraints:
        structured_constraints = parse_constraints(request.constraints)

    # STEP 2 — Build schedule
    schedule = build_schedule(
        sessions=[s.dict() for s in request.sessions],
        venues=[v.dict() for v in request.venues]
    )

    # STEP 3 — Apply constraint optimizer
    if structured_constraints:
        schedule = apply_constraints(schedule, structured_constraints)

    # STEP 4 — Detect conflicts
    conflicts = detect_conflicts(schedule)

    resolutions = []

    # STEP 5 — Resolve conflicts
    if conflicts:
        schedule, resolutions = resolve_conflicts(schedule, conflicts)

    # STEP 6 — Optional what‑if simulation
    simulation_result = None

    if hasattr(request, "what_if") and request.what_if:

        simulation_result = simulate_change(
            schedule,
            request.what_if.get("session_id"),
            request.what_if.get("new_time")
        )

    # STEP 7 — Generate reasoning
    llm = get_llm()

    reasoning_prompt = f"""
You are Chronos, an AI scheduling intelligence.

Analyze the schedule and explain the reasoning.

Event Name:
{request.event_name}

Generated Schedule:
{schedule}

Constraints Interpreted:
{structured_constraints}

Conflicts Detected:
{conflicts}

Resolutions Applied:
{resolutions}

If constraints were enforced, explain how they changed the schedule.

Explain briefly and clearly.
"""

    reasoning = llm.invoke(reasoning_prompt).content

    # STEP 8 — Cascade triggers
    cascade = []

    if resolutions:
        cascade = ["hermes_agent", "apollo_agent"]

    # STEP 9 — Return result
    return ScheduleResult(
        timeline=schedule,
        conflicts_found=conflicts,
        conflicts_resolved=resolutions,
        warnings=[],
        affected_participants=[],
        cascade_to=cascade,
        reasoning=reasoning,
        simulation=simulation_result
    )