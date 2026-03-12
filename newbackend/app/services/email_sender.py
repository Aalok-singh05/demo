# Email sending service — mock mode by default, real SMTP optional

import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Send a single email. Uses mock mode by default (logs instead of sending).
    Set EMAIL_REAL_SEND=true in .env for actual SMTP sending.
    """
    if settings.EMAIL_REAL_SEND:
        return await _send_real(to, subject, body)
    else:
        return _send_mock(to, subject, body)


def _send_mock(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Log the email instead of actually sending it (demo mode)."""
    logger.info(f"📧 [MOCK] Email to: {to} | Subject: {subject}")
    return {
        "status": "sent_mock",
        "to": to,
        "subject": subject,
        "message": "Email logged (mock mode). Set EMAIL_REAL_SEND=true for real sending.",
    }


async def _send_real(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Send via SMTP (requires aiosmtplib — uncomment in requirements.txt)."""
    try:
        import aiosmtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME or None,
            password=settings.SMTP_PASSWORD or None,
        )
        return {"status": "sent", "to": to, "subject": subject}

    except ImportError:
        logger.warning("aiosmtplib not installed — falling back to mock mode")
        return _send_mock(to, subject, body)
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return {"status": "error", "to": to, "error": str(e)}


async def send_batch(emails: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Send a batch of emails.
    Each item: {"to": "...", "subject": "...", "body": "..."}
    """
    results = []
    sent = 0
    failed = 0

    for email in emails:
        result = await send_email(email["to"], email["subject"], email["body"])
        results.append(result)
        if "error" in result.get("status", ""):
            failed += 1
        else:
            sent += 1

    return {"total": len(emails), "sent": sent, "failed": failed, "results": results}
