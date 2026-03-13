# ============================================================================
# NEXUS BACKEND — Hermes Mail Agent
# ============================================================================
# Hermes is responsible for:
# - Parsing participant data
# - Validating emails
# - Segmenting participants
# - Personalizing templates
# - Sending batch emails
# ============================================================================

from app.schemas.hermes_schema import MailRequest, MailResult, EmailPreview

from app.services.csv_parser import parse_participant_file
from app.services.email_validator import validate_email_batch
from app.services.segmentation import segment_by_field, segment_by_criteria, create_segment_summary
from app.services.template_engine import personalize_batch
from app.services.email_sender import send_batch

from app.services.llm_service import get_llm


async def hermes_agent(request: MailRequest) -> MailResult:

    participants = []
    invalid_emails = []
    segments = []
    previews = []

    # ==========================================================
    # ACTION 1 — PARSE DATA
    # ==========================================================
    if request.action == "parse_data":

        result = await parse_participant_file(request.data_file)

        participants = result["participants"]
        invalid_emails = result["invalid_details"]

        return MailResult(
            action_completed="Participant data parsed",
            participants_processed=result["valid"],
            invalid_emails=invalid_emails,
            reasoning="Hermes parsed the uploaded CSV and validated participant emails."
        )

    # ==========================================================
    # ACTION 2 — SEGMENT PARTICIPANTS
    # ==========================================================
    if request.action == "segment":

        if not request.recipients:
            return MailResult(
                action_completed="Segmentation skipped",
                reasoning="No participants provided for segmentation."
            )

        participants = request.recipients

        if request.segment_criteria:

            filtered = segment_by_criteria(participants, request.segment_criteria)

            segments = [
                {
                    "name": request.segment_criteria,
                    "count": len(filtered)
                }
            ]

        else:

            segmented = segment_by_field(participants, "role")

            segments = create_segment_summary(segmented)

        return MailResult(
            action_completed="Participants segmented",
            participants_processed=len(participants),
            segments_created=segments,
            reasoning="Hermes grouped participants according to the requested segmentation rules."
        )

    # ==========================================================
    # ACTION 3 — PERSONALIZE EMAIL TEMPLATE
    # ==========================================================
    if request.action == "personalize":

        if not request.recipients or not request.base_template:
            return MailResult(
                action_completed="Personalization failed",
                reasoning="Recipients or base template missing."
            )

        participants = request.recipients

        preview_data = personalize_batch(
            request.base_template,
            participants
        )

        for p in preview_data["previews"]:
            previews.append(
                EmailPreview(
                    to=p["to"],
                    subject="Event Update",
                    body=p["body"]
                )
            )

        return MailResult(
            action_completed="Emails personalized",
            participants_processed=preview_data["total"],
            preview_emails=previews,
            ready_to_send=False,
            requires_approval=True,
            reasoning="Hermes generated personalized email previews using the template engine."
        )

    # ==========================================================
    # ACTION 4 — SEND EMAILS
    # ==========================================================
    if request.action == "send":

        if not request.recipients or not request.base_template:
            return MailResult(
                action_completed="Send failed",
                reasoning="Missing recipients or template."
            )

        participants = request.recipients

        # Generate full personalized emails
        emails = []

        for p in participants:

            subject = "Event Notification"

            body = request.base_template.replace(
                "{{name}}",
                p.get("name", "Participant")
            )

            emails.append({
                "to": p.get("email"),
                "subject": subject,
                "body": body
            })

        send_result = await send_batch(emails)

        return MailResult(
            action_completed="Emails sent",
            participants_processed=send_result["sent"],
            reasoning="Hermes dispatched the email batch using the email sender service.",
            requires_approval=False,
            ready_to_send=False
        )

    # ==========================================================
    # DEFAULT FALLBACK
    # ==========================================================

    return MailResult(
        action_completed="No action executed",
        reasoning="The requested Hermes action was not recognized."
    )