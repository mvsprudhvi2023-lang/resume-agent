import json

import pytest

from app import agents
from app.orchestrator import PipelineError, run_pipeline

PARSED = {
    "job_title": "AI Business Analyst",
    "required_skills": ["Python", "SQL", "Power BI"],
    "nice_to_have_skills": [],
    "keywords": ["Python"],
}
RESUME = {
    "professional_summary": "Summary",
    "key_skills": ["Python"],
    "highlights": [],
    "missing_skills": ["Power BI"],
}
REVIEW = {
    "ats_score": 60,
    "matched_keywords": [],
    "missing_keywords": [],
    "unsupported_claims": [],
    "suggestions": [],
}

CANDIDATE = {
    "full_name": "Test Person",
    "skills": ["Python"],
    "experience_years": 3,
    "achievements": ["Built a small bot"],
}
JOB = "We need a Python analyst. Email hr@example.com or call +1 555 123 4567."


def make_fake_llm(prompts):
    def fake_llm(prompt):
        prompts.append(prompt)
        if "job description parser" in prompt:
            return json.dumps(PARSED)
        if "professional resume writer" in prompt:
            return json.dumps(RESUME)
        return json.dumps(REVIEW)

    return fake_llm


def test_pipeline_returns_all_parts(monkeypatch):
    monkeypatch.setattr(agents, "ask_llm", make_fake_llm([]))
    result = run_pipeline(CANDIDATE, JOB)
    assert set(result) == {"parsed_job", "resume", "review", "steps"}
    assert [s["step"] for s in result["steps"]] == [
        "parse_job",
        "write_resume",
        "review_resume",
    ]


def test_pii_and_name_never_reach_the_model(monkeypatch):
    prompts = []
    monkeypatch.setattr(agents, "ask_llm", make_fake_llm(prompts))
    run_pipeline(CANDIDATE, JOB)
    everything = " ".join(prompts)
    assert "hr@example.com" not in everything
    assert "555 123 4567" not in everything
    assert "Test Person" not in everything
    assert "[EMAIL]" in everything


def test_invalid_json_stops_the_pipeline(monkeypatch):
    monkeypatch.setattr(agents, "ask_llm", lambda prompt: "this is not json")
    with pytest.raises(PipelineError) as error:
        run_pipeline(CANDIDATE, JOB)
    assert error.value.step == "parse_job"