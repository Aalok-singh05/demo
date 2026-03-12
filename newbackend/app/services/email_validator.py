# Email validation service

import re
from typing import List, Tuple


def validate_email(email: str) -> bool:
    """Check if an email address has valid format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_email_batch(emails: List[str]) -> Tuple[List[str], List[dict]]:
    """
    Validate a batch of emails.
    Returns (valid_emails, invalid_entries).
    """
    valid = []
    invalid = []

    for email in emails:
        email = email.strip().lower()
        if validate_email(email):
            valid.append(email)
        else:
            reason = "Missing email" if not email else "Invalid format"
            invalid.append({"email": email, "reason": reason})

    return valid, invalid


def find_duplicates(emails: List[str]) -> Tuple[List[str], List[str]]:
    """
    Find duplicate emails.
    Returns (unique_emails, duplicate_emails).
    """
    seen = set()
    unique = []
    dupes = []

    for email in emails:
        email_lower = email.strip().lower()
        if email_lower in seen:
            dupes.append(email_lower)
        else:
            seen.add(email_lower)
            unique.append(email_lower)

    return unique, dupes
