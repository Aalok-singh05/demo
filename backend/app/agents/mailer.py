"""Hermes — The Mail Agent.

Parses CSV/Excel uploads, validates emails, personalizes templates.
Falls back to rule-based processing if LLM is unavailable.
"""
import io
import re
from ..models.schemas import Participant, UploadResult, PersonalizeResult, EmailPreview
from .llm_helper import call_llm

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


async def parse_and_validate_csv(content: bytes, ext: str, filename: str) -> UploadResult:
    """Parse a CSV/Excel file and validate participant data.
    
    Args:
        content: Raw file bytes.
        ext: File extension ('csv', 'xlsx', 'xls').
        filename: Original filename.
    
    Returns:
        UploadResult with parsed participants and validation stats.
    """
    participants = []
    invalid_count = 0
    duplicate_emails = set()
    seen_emails = set()

    if PANDAS_AVAILABLE:
        try:
            if ext == "csv":
                df = pd.read_csv(io.BytesIO(content))
            else:
                df = pd.read_excel(io.BytesIO(content))

            # Normalize column names
            col_map = _normalize_columns(df.columns.tolist())
            df = df.rename(columns=col_map)

            for idx, row in df.iterrows():
                name = str(row.get("name", row.get("full_name", f"Participant {idx+1}")))
                email = str(row.get("email", ""))
                role = str(row.get("role", row.get("type", "attendee"))).lower()

                # Validate email
                is_valid = _validate_email(email)

                # Check duplicates
                if email.lower() in seen_emails:
                    duplicate_emails.add(email.lower())
                    continue
                seen_emails.add(email.lower())

                status = "valid" if is_valid else "invalid"
                if not is_valid:
                    invalid_count += 1

                participants.append(Participant(
                    id=idx + 1,
                    name=name.strip(),
                    email=email.strip(),
                    role=role.strip(),
                    status=status
                ))
        except Exception as e:
            # Fallback: return error info
            return UploadResult(
                total_parsed=0, valid_emails=0,
                invalid_emails=0, duplicates=0,
                participants=[]
            )
    else:
        # Minimal CSV parsing without pandas
        lines = content.decode("utf-8", errors="replace").strip().split("\n")
        if lines:
            header = [h.strip().lower() for h in lines[0].split(",")]
            name_col = _find_col(header, ["name", "full_name", "participant"])
            email_col = _find_col(header, ["email", "e-mail", "mail"])
            role_col = _find_col(header, ["role", "type", "category"])

            for idx, line in enumerate(lines[1:], 1):
                parts = [p.strip() for p in line.split(",")]
                name = parts[name_col] if name_col is not None and name_col < len(parts) else f"Participant {idx}"
                email = parts[email_col] if email_col is not None and email_col < len(parts) else ""
                role = parts[role_col] if role_col is not None and role_col < len(parts) else "attendee"

                is_valid = _validate_email(email)
                if email.lower() in seen_emails:
                    duplicate_emails.add(email.lower())
                    continue
                seen_emails.add(email.lower())

                status = "valid" if is_valid else "invalid"
                if not is_valid:
                    invalid_count += 1

                participants.append(Participant(
                    id=idx, name=name, email=email,
                    role=role.lower(), status=status
                ))

    valid_count = len(participants) - invalid_count
    return UploadResult(
        total_parsed=len(participants),
        valid_emails=valid_count,
        invalid_emails=invalid_count,
        duplicates=len(duplicate_emails),
        participants=participants
    )


async def personalize_emails(
    template: str, participants: list[dict]
) -> PersonalizeResult:
    """Personalize an email template for each participant.
    
    Args:
        template: Email template with {{placeholder}} fields.
        participants: List of participant dicts.
    
    Returns:
        PersonalizeResult with previews and total count.
    """
    previews = []
    for p in participants[:5]:  # Preview first 5
        body = template
        body = body.replace("{{name}}", p.get("name", ""))
        body = body.replace("{{role}}", p.get("role", "attendee").title())
        body = body.replace("{{email}}", p.get("email", ""))
        body = body.replace("{{first_session_time}}", "09:00 AM")
        body = body.replace("{{first_room}}", "Main Hall")

        previews.append(EmailPreview(
            recipient_name=p.get("name", ""),
            recipient_email=p.get("email", ""),
            subject="TechSummit 2026 — Your Registration Details",
            body=body
        ))

    return PersonalizeResult(
        previews=previews,
        total_recipients=len(participants)
    )


def _validate_email(email: str) -> bool:
    """Basic email format validation."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def _normalize_columns(columns: list[str]) -> dict[str, str]:
    """Map common column name variants to standard names."""
    mapping = {}
    for col in columns:
        lower = col.strip().lower().replace(" ", "_")
        if lower in ("name", "full_name", "participant_name", "first_name"):
            mapping[col] = "name"
        elif lower in ("email", "e-mail", "email_address", "mail"):
            mapping[col] = "email"
        elif lower in ("role", "type", "category", "participant_type"):
            mapping[col] = "role"
    return mapping


def _find_col(header: list[str], candidates: list[str]) -> int | None:
    """Find column index matching any candidate name."""
    for i, h in enumerate(header):
        if h.strip().lower() in candidates:
            return i
    return None
