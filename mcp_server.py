from mcp.server.fastmcp import FastMCP

from app.agents import parse_job_description
from app.privacy import mask_pii

mcp = FastMCP("Resume Tools")


@mcp.tool()
def mask_pii_text(text: str) -> str:
    """Replace emails and phone numbers in the text with [EMAIL] and [PHONE]."""
    return mask_pii(text)


@mcp.tool()
def skill_match(candidate_skills: list[str], required_skills: list[str]) -> dict:
    """Compare a candidate's skills with the skills a job requires."""
    have = {s.strip().lower() for s in candidate_skills}
    matched = [s for s in required_skills if s.strip().lower() in have]
    missing = [s for s in required_skills if s.strip().lower() not in have]
    percent = round(100 * len(matched) / len(required_skills)) if required_skills else 0
    return {"matched": matched, "missing": missing, "match_percent": percent}


@mcp.tool()
def parse_job(job_description: str) -> dict:
    """Extract the job title, required skills and keywords from a job description."""
    return parse_job_description(mask_pii(job_description))


if __name__ == "__main__":
    mcp.run(transport="stdio")