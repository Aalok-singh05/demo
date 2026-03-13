import asyncio

from app.schemas.hermes_schema import MailRequest
from app.agents.hermes_agent import hermes_agent


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_previews(previews):

    if not previews:
        print("No preview emails generated.")
        return

    for i, email in enumerate(previews, start=1):

        print(f"\n--- Preview {i} ---")
        print(f"To: {email.to}")
        print(f"Subject: {email.subject}")
        print("\nBody:")
        print(email.body)


async def run_test_case(name, request):

    print_section(f"TEST: {name}")

    result = await hermes_agent(request)

    print("\n--- ACTION COMPLETED ---")
    print(result.action_completed)

    print("\nParticipants Processed:", result.participants_processed)

    if result.invalid_emails:
        print("\n--- INVALID EMAILS ---")
        for e in result.invalid_emails:
            print(e)

    if result.segments_created:
        print("\n--- SEGMENTS CREATED ---")
        for seg in result.segments_created:
            print(seg)

    if result.preview_emails:
        print("\n--- EMAIL PREVIEWS ---")
        print_previews(result.preview_emails)

    print("\nReady To Send:", result.ready_to_send)
    print("Requires Approval:", result.requires_approval)

    print("\n--- REASONING ---")
    print(result.reasoning)


async def main():

    # -------------------------------------------------
    # TEST PARTICIPANT DATA
    # -------------------------------------------------

    participants = [
        {
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "role": "attendee",
            "track": "AI"
        },
        {
            "name": "Priya Mehta",
            "email": "priya@example.com",
            "role": "speaker",
            "track": "Robotics"
        },
        {
            "name": "Arjun Singh",
            "email": "arjun@example.com",
            "role": "attendee",
            "track": "AI"
        }
    ]

    template = """
Hello {{first_name}},

We are excited to invite you to the Neurathon AI Hackathon.

Your role: {{role}}
Track: {{track}}

See you there!

— Nexus Team
"""

    # -------------------------------------------------
    # TEST 1 — SEGMENTATION
    # -------------------------------------------------

    request_segment = MailRequest(
        action="segment",
        recipients=participants,
        segment_criteria="speaker"
    )

    await run_test_case("Participant Segmentation", request_segment)

    # -------------------------------------------------
    # TEST 2 — PERSONALIZATION
    # -------------------------------------------------

    request_personalize = MailRequest(
        action="personalize",
        recipients=participants,
        base_template=template
    )

    await run_test_case("Email Personalization", request_personalize)

    # -------------------------------------------------
    # TEST 3 — EMAIL SENDING
    # -------------------------------------------------

    request_send = MailRequest(
        action="send",
        recipients=participants,
        base_template=template
    )

    await run_test_case("Email Sending", request_send)


if __name__ == "__main__":
    asyncio.run(main())