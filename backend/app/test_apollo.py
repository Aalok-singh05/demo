from app.schemas.apollo_schema import ContentRequest
from app.agents.apollo_agent import apollo_agent


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_content_pieces(pieces):

    if not pieces:
        print("No content pieces generated.")
        return

    for i, piece in enumerate(pieces, start=1):

        print(f"\n--- Variant {i} ---")
        print(f"Platform: {piece.platform}")
        print(f"Suggested Time: {piece.suggested_time}")

        print("\nTEXT:")
        print(piece.text)

        if getattr(piece, "image_prompt", None):
            print("\nImage Prompt:")
            print(piece.image_prompt)


def run_test_case(name, request):

    print_section(f"TEST: {name}")

    result = apollo_agent(request)

    if result.content_pieces:
        print("\n--- GENERATED CONTENT ---")
        print_content_pieces(result.content_pieces)

    if result.campaign_timeline:
        print("\n--- CAMPAIGN TIMELINE ---")
        for step in result.campaign_timeline:
            print(step)

    if result.engagement_insights:
        print("\n--- ENGAGEMENT INSIGHTS ---")
        print(result.engagement_insights)

    print("\n--- REASONING ---")
    print(result.reasoning)


def main():

    # -------------------------------------------------
    # TEST 1 — CONTENT GENERATION
    # -------------------------------------------------

    request_generate = ContentRequest(
        action="generate",
        event_description="Neurathon AI Hackathon for university students focusing on AI, robotics and innovation.",
        target_audience="Computer science students and AI enthusiasts",
        platform="twitter"
    )

    run_test_case("Content Generation", request_generate)

    # -------------------------------------------------
    # TEST 2 — CAMPAIGN PLANNING
    # -------------------------------------------------

    request_campaign = ContentRequest(
        action="plan_campaign",
        event_description="Neurathon AI Hackathon for university students."
    )

    run_test_case("Campaign Planning", request_campaign)

    # -------------------------------------------------
    # TEST 3 — ENGAGEMENT ANALYSIS
    # -------------------------------------------------

    request_analysis = ContentRequest(
        action="analyze_timing",
        event_description="Neurathon AI Hackathon",
        historical_data="engagement_sample.csv"
    )

    run_test_case("Engagement Analysis", request_analysis)

    # -------------------------------------------------
    # TEST 4 — CONTENT UPDATE
    # -------------------------------------------------

    request_update = ContentRequest(
        action="update_content",
        event_description="Neurathon AI Hackathon (Date changed to next weekend)",
        platform="linkedin",
        existing_content_id="demo_post_123"
    )

    run_test_case("Content Update", request_update)


if __name__ == "__main__":
    main()