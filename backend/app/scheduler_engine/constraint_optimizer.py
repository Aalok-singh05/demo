from datetime import datetime, timedelta


def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")


def format_time(time_obj):
    return time_obj.strftime("%H:%M")


def apply_constraints(schedule, constraints):
    """
    Enforce scheduling constraints on an already generated schedule.
    """

    if not constraints:
        return schedule

    for rule in constraints:

        rule_type = rule.get("type")

        # -----------------------------
        # START AFTER CONSTRAINT
        # -----------------------------
        if rule_type == "start_after":

            speaker = rule.get("speaker")
            time_limit = parse_time(rule.get("time"))

            for session in schedule:

                if session["speaker"] == speaker:

                    start = parse_time(session["start_time"])
                    end = parse_time(session["end_time"])

                    duration = end - start

                    if start < time_limit:

                        new_start = time_limit
                        new_end = new_start + duration

                        session["start_time"] = format_time(new_start)
                        session["end_time"] = format_time(new_end)

        # -----------------------------
        # START BEFORE CONSTRAINT
        # -----------------------------
        if rule_type == "start_before":

            speaker = rule.get("speaker")
            time_limit = parse_time(rule.get("time"))

            for session in schedule:

                if session["speaker"] == speaker:

                    start = parse_time(session["start_time"])
                    end = parse_time(session["end_time"])

                    duration = end - start

                    if start > time_limit:

                        new_end = time_limit
                        new_start = new_end - duration

                        session["start_time"] = format_time(new_start)
                        session["end_time"] = format_time(new_end)

        # -----------------------------
        # MUST BE ON DAY
        # -----------------------------
        if rule_type == "must_be_on_day":

            speaker = rule.get("speaker")
            target_day = rule.get("day")

            for session in schedule:

                if session["speaker"] == speaker:
                    session["day"] = target_day

        # -----------------------------
        # CANNOT BE ON DAY
        # -----------------------------
        if rule_type == "cannot_be_on_day":

            speaker = rule.get("speaker")
            forbidden_day = rule.get("day")

            for session in schedule:

                if session["speaker"] == speaker:

                    if session["day"] == forbidden_day:
                        session["day"] += 1

        # -----------------------------
        # PREFERRED ROOM
        # -----------------------------
        if rule_type == "preferred_room":

            speaker = rule.get("speaker")
            preferred_room = rule.get("room")

            for session in schedule:

                if session["speaker"] == speaker:
                    session["room"] = preferred_room

    return schedule