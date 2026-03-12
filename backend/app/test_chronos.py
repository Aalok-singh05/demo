from app.schemas.chronos_schema import ScheduleRequest
from app.schemas.shared_models import Session, Venue
from app.agents.chronos_agent import chronos_agent


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def run_test_case(name, request):
    print_section(f"TEST: {name}")

    result = chronos_agent(request)

    print("\n--- GENERATED SCHEDULE ---")
    for s in result.timeline:
        print(
            f"Day {s.day} | {s.start_time} - {s.end_time} | "
            f"{s.room} | {s.title} ({s.speaker})"
        )

    print("\n--- CONFLICTS DETECTED ---")
    print(result.conflicts_found)

    print("\n--- RESOLUTIONS ---")
    print(result.conflicts_resolved)

    print("\n--- CASCADE TRIGGERS ---")
    print(result.cascade_to)

    print("\n--- REASONING ---")
    print(result.reasoning)

    # -----------------------------
    # WHAT IF SIMULATION OUTPUT
    # -----------------------------

    if hasattr(result, "simulation") and result.simulation:

        print("\n--- WHAT IF SIMULATION ---")

        sim = result.simulation

        print("\nMoved Session:")
        print(sim["moved_session"])

        print("\nConflicts After Change:")
        print(sim["conflicts"])

        print("\nSimulated Schedule:")

        for s in sim["simulated_schedule"]:
            print(
                f"Day {s['day']} | {s['start_time']} - {s['end_time']} | "
                f"{s['room']} | {s['title']} ({s['speaker']})"
            )


def main():

    venues = [
        Venue(name="Hall A", capacity=100),
        Venue(name="Hall B", capacity=80),
    ]

    # -------------------------------------------------
    # TEST 1 — BASIC SCHEDULE
    # -------------------------------------------------

    sessions_basic = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=3,
            day=1
        ),

        Session(
            session_id="S2",
            title="LLM Workshop",
            speaker="Dr Gupta",
            duration_minutes=60,
            priority=2,
            day=1
        ),

        Session(
            session_id="S3",
            title="Robotics",
            speaker="Dr Mehta",
            duration_minutes=60,
            priority=1,
            day=2
        )
    ]

    request1 = ScheduleRequest(
        event_name="Basic Schedule",
        days=3,
        sessions=sessions_basic,
        venues=venues,
        constraints=[]
    )

    run_test_case("Basic Schedule Generation", request1)

    # -------------------------------------------------
    # TEST 2 — SPEAKER CONFLICT
    # -------------------------------------------------

    sessions_speaker_conflict = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=3,
            day=1
        ),

        Session(
            session_id="S2",
            title="Deep Learning",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=2,
            day=1
        )
    ]

    request2 = ScheduleRequest(
        event_name="Speaker Conflict",
        days=2,
        sessions=sessions_speaker_conflict,
        venues=[Venue(name="Hall A", capacity=100)],
        constraints=[]
    )

    run_test_case("Speaker Conflict Detection", request2)

    # -------------------------------------------------
    # TEST 3 — ROOM CONFLICT
    # -------------------------------------------------

    sessions_room_conflict = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=1,
            day=1
        ),

        Session(
            session_id="S2",
            title="LLM Workshop",
            speaker="Dr Gupta",
            duration_minutes=60,
            priority=1,
            day=1
        )
    ]

    request3 = ScheduleRequest(
        event_name="Room Conflict",
        days=2,
        sessions=sessions_room_conflict,
        venues=[Venue(name="Hall A", capacity=100)],
        constraints=[]
    )

    run_test_case("Room Conflict Resolution", request3)

    # -------------------------------------------------
    # TEST 4 — CROSS DAY SCHEDULING
    # -------------------------------------------------

    sessions_cross_day = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=120,
            priority=3,
            day=1
        ),

        Session(
            session_id="S2",
            title="LLM Workshop",
            speaker="Dr Gupta",
            duration_minutes=120,
            priority=2,
            day=1
        ),

        Session(
            session_id="S3",
            title="Robotics",
            speaker="Dr Mehta",
            duration_minutes=120,
            priority=1,
            day=1
        ),

        Session(
            session_id="S4",
            title="Computer Vision",
            speaker="Dr Singh",
            duration_minutes=120,
            priority=1,
            day=1
        )
    ]

    request4 = ScheduleRequest(
        event_name="Cross Day Movement",
        days=3,
        sessions=sessions_cross_day,
        venues=[Venue(name="Hall A", capacity=100)],
        constraints=[]
    )

    run_test_case("Cross Day Scheduling", request4)

    # -------------------------------------------------
    # TEST 5 — NATURAL LANGUAGE CONSTRAINT
    # -------------------------------------------------

    sessions_constraint = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=2,
            day=1
        ),

        Session(
            session_id="S2",
            title="Robotics",
            speaker="Dr Mehta",
            duration_minutes=60,
            priority=1,
            day=1
        )
    ]

    request5 = ScheduleRequest(
        event_name="Constraint Test",
        days=2,
        sessions=sessions_constraint,
        venues=venues,
        constraints=[
            "Dr Sharma only available after 14:00"
        ]
    )

    run_test_case("Natural Language Constraint", request5)

    # -------------------------------------------------
    # TEST 6 — WHAT IF SIMULATION
    # -------------------------------------------------

    sessions_whatif = [

        Session(
            session_id="S1",
            title="AI Ethics",
            speaker="Dr Sharma",
            duration_minutes=60,
            priority=2,
            day=1
        ),

        Session(
            session_id="S2",
            title="Robotics",
            speaker="Dr Mehta",
            duration_minutes=60,
            priority=1,
            day=1
        )
    ]

    request6 = ScheduleRequest(
        event_name="What If Test",
        days=2,
        sessions=sessions_whatif,
        venues=venues,
        constraints=[],
        what_if={
            "session_id": "S1",
            "new_time": "15:00"
        }
    )

    run_test_case("What If Simulation", request6)


if __name__ == "__main__":
    main()