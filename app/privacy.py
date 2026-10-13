import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().\-]{7,}\d(?!\w)")


def _digits(text: str) -> int:
    return len(re.sub(r"\D", "", text))


def _mask_phone(match) -> str:
    # Only treat it as a phone number if it has at least 10 digits.
    # This keeps date ranges like "2019 - 2023" safe.
    return "[PHONE]" if _digits(match.group()) >= 10 else match.group()


def mask_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub(_mask_phone, text)
    return text


def count_pii(text: str) -> dict:
    emails = len(EMAIL_RE.findall(text))
    without_emails = EMAIL_RE.sub("", text)
    phones = sum(1 for m in PHONE_RE.finditer(without_emails) if _digits(m.group()) >= 10)
    return {"emails": emails, "phones": phones}