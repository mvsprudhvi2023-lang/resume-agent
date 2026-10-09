import json
from app.llm import ask_llm


def parse_job_description(job_description: str) -> dict:
    prompt = f"""You are a job description parser.
Read the job description below and return ONLY valid JSON with these keys:
- job_title (string)
- required_skills (list of strings)
- nice_to_have_skills (list of strings)
- keywords (list of strings useful for ATS resume scanners)

Job description:
{job_description}
"""
    text = ask_llm(prompt).strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON", "raw": text}