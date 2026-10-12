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



def review_resume(candidate: dict, parsed_job: dict, resume: dict) -> dict:
    prompt = f"""You are a strict resume reviewer.
Compare the resume content with the target job and the candidate's real facts.

RULES:
- Suggestions must never tell the candidate to claim skills or experience they do not have.
- If something is missing, suggest learning it or gaining it honestly.

Return ONLY valid JSON with these keys:
- ats_score (integer from 0 to 100, how well the resume matches the job keywords)
- matched_keywords (list of job keywords that appear in the resume)
- missing_keywords (list of job keywords that do not appear in the resume)
- unsupported_claims (list of statements in the resume that are NOT supported by the candidate facts, empty list if none)
- suggestions (list of up to 3 short, honest suggestions)

Candidate facts:
{json.dumps(candidate, indent=2)}

Target job (parsed):
{json.dumps(parsed_job, indent=2)}

Resume content:
{json.dumps(resume, indent=2)}
"""
    return _to_json(ask_llm(prompt))