from app.schemas.chronos_schema import (
    ScheduleRequest,
    ScheduleResult,
    ScheduledSession,
    Conflict,
    Resolution
)

from app.scheduler_engine.schedule_builder import build_schedule
from app.scheduler_engine.constraint_parser import parse_constraints
from app.scheduler_engine.constraint_optimizer import apply_constraints
from app.scheduler_engine.conflict_detector import detect_conflicts
from app.scheduler_engine.resolution_engine import resolve_conflicts

from app.services.llm_service import get_llm


def chronos_agent(request: ScheduleRequest) -> ScheduleResult:

    reasoning_steps = []
    reasoning_steps.append("Initializing Chronos scheduling engine")

    # ------------------------------------------------
    # STEP 1 — BUILD INITIAL SCHEDULE
    # ------------------------------------------------

    schedule = build_schedule(
        sessions=request.sessions,
        venues=request.venues,
        fixed_slots=request.fixed_slots,
        days=request.days
    )

    reasoning_steps.append(
        f"Generated initial schedule with {len(schedule)} sessions"
    )

    # ------------------------------------------------
    # STEP 2 — PARSE CONSTRAINTS
    # ------------------------------------------------

    structured_constraints = []

    if request.constraints:
        structured_constraints = parse_constraints(request.constraints)

    reasoning_steps.append(
        f"Parsed {len(structured_constraints)} scheduling constraints"
    )

    # ------------------------------------------------
    # STEP 3 — APPLY CONSTRAINTS
    # ------------------------------------------------

    warnings = []

    if structured_constraints:

        reasoning_steps.append("Applying scheduling constraints")

        schedule, warnings = apply_constraints(schedule, structured_constraints)

        for w in warnings:
            reasoning_steps.append(f"Constraint adjustment: {w}")

    # ------------------------------------------------
    # STEP 4 — DETECT CONFLICTS
    # ------------------------------------------------

    raw_conflicts = detect_conflicts(schedule)

    conflicts = []
    resolutions = []

    if raw_conflicts:
        reasoning_steps.append(
            f"Detected {len(raw_conflicts)} scheduling conflicts"
        )
    else:
        reasoning_steps.append("No conflicts detected in schedule")

    # Convert raw conflicts to schema objects

    for c in raw_conflicts:

        conflicts.append(
            Conflict(
                type=c.get("type"),
                severity=c.get("severity"),
                description=c.get("description"),
                sessions_involved=c.get("sessions_involved", [])
            )
        )

    # ------------------------------------------------
    # STEP 5 — RESOLVE CONFLICTS
    # ------------------------------------------------

    if raw_conflicts:

        reasoning_steps.append("Attempting to resolve scheduling conflicts")

        venue_names = [v.name for v in request.venues]

        schedule, raw_resolutions = resolve_conflicts(
            schedule,
            conflicts,
            venue_names,
            request.days
        )

        for r in raw_resolutions:

            resolutions.append(
                Resolution(
                    conflict_type=r.conflict_type,
                    action_taken=r.action_taken,
                    sessions_moved=r.sessions_moved,
                    participants_affected=r.participants_affected
                )
            )

            reasoning_steps.append(r.action_taken)

    reasoning_steps.append("Schedule finalized successfully")

    # ------------------------------------------------
    # STEP 6 — CONVERT TO TIMELINE
    # ------------------------------------------------

    timeline = []

    for s in schedule:

        timeline.append(
            ScheduledSession(
                id=str(s["id"]),
                title=s["title"],
                session_type=s.get("session_type", "talk"),
                speaker=s.get("speaker"),
                venue=s.get("venue"),
                day=int(s.get("day")),
                start_time=s.get("start_time"),
                end_time=s.get("end_time"),
                capacity=s.get("capacity"),
                status=s.get("status", "scheduled")
            )
        )

    # ------------------------------------------------
    # STEP 7 — GENERATE REASONING SUMMARY
    # ------------------------------------------------

    llm = get_llm()

    reasoning_prompt = f"""
You are Chronos, an AI scheduling intelligence.

Explain the scheduling outcome briefly.

Event:
{request.event_name}

Reasoning Steps:
{reasoning_steps}

Final Timeline:
{timeline}

Conflicts:
{conflicts}

Resolutions:
{resolutions}

Provide a short explanation.
"""

    reasoning_summary = llm.invoke(reasoning_prompt).content

    reasoning = "\n".join(reasoning_steps) + "\n\n" + reasoning_summary

    # ------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------

    return ScheduleResult(
        timeline=timeline,
        conflicts_found=conflicts,
        conflicts_resolved=resolutions,
        warnings=warnings,
        reasoning=reasoning
    )


def remove_session(schedule, session_id):
    """
    Remove a session directly from the timeline.
    """

    updated_schedule = [
        s for s in schedule if s["id"] != session_id
    ]

    return {
        "status": "session_removed",
        "removed_session": session_id,
        "updated_schedule": updated_schedule
    }