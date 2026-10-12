import json
from app.llm import ask_llm


def _to_json(text: str) -> dict:
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Model did not return valid JSON", "raw": text}


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
    return _to_json(ask_llm(prompt))


def write_resume_content(candidate: dict, parsed_job: dict) -> dict:
    prompt = f"""You are a professional resume writer.
Write resume content for the candidate, tailored to the target job.

STRICT RULES:
- Use ONLY the facts given about the candidate.
- Do NOT invent employers, degrees, tools, numbers or achievements.
- Include the job keywords that match the candidate's real skills.
- If the candidate gave no achievements, return an empty list for highlights.
- Do NOT claim results, impact or success unless the candidate stated them.
- experience_years is the candidate's TOTAL years of experience. Never say they have that many years with a specific tool.
- Keep the original meaning of each achievement. Do not make it sound bigger. Use plain verbs like built, created, set up.

Return ONLY valid JSON with these keys:
- professional_summary (string, 2 to 3 sentences)
- key_skills (list of strings, only skills the candidate listed)
- highlights (list of strings, the candidate's achievements rewritten in a strong action-verb style)
- missing_skills (list of strings, required skills in the job that the candidate did not list)

Candidate:
{json.dumps(candidate, indent=2)}

Target job (parsed):
{json.dumps(parsed_job, indent=2)}
"""
    return _to_json(ask_llm(prompt))