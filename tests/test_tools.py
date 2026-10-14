from app.privacy import mask_pii, count_pii
from mcp_server import skill_match


def test_masks_email():
    assert mask_pii("Mail hr@example.com now") == "Mail [EMAIL] now"


def test_masks_phone_number():
    assert mask_pii("Call +1 555 123 4567 today") == "Call [PHONE] today"


def test_keeps_date_ranges():
    text = "Worked 2019 - 2023 at a company"
    assert mask_pii(text) == text


def test_count_pii():
    assert count_pii("hr@example.com and +1 555 123 4567") == {"emails": 1, "phones": 1}


def test_skill_match_percent():
    result = skill_match(["Python", "SQL"], ["Python", "SQL", "Power BI"])
    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == ["Power BI"]
    assert result["match_percent"] == 67


def test_skill_match_ignores_case_and_spaces():
    result = skill_match([" python "], ["Python"])
    assert result["match_percent"] == 100