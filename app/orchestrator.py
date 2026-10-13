import time
from app.agents import parse_job_description, write_resume_content, review_resume
from app.audit import logger
from app.privacy import mask_pii, count_pii


class PipelineError(Exception):
    def __init__(self, step: str, detail: dict):
        self.step = step
        self.detail = detail
        super().__init__(f"Step '{step}' failed")


def run_pipeline(candidate: dict, job_description: str) -> dict:
    steps = []

    # Mask personal data before it goes to the model. Log counts only, never the content.
    logger.info("PII found in job description: %s", count_pii(job_description))
    safe_job = mask_pii(job_description)

    # Data minimization: the model does not need the name, so it is not sent.
    safe_candidate = {
        "skills": candidate["skills"],
        "experience_years": candidate["experience_years"],
        "achievements": [mask_pii(a) for a in candidate.get("achievements", [])],
    }

    def run_step(name, func, *args):
        start = time.time()
        try:
            result = func(*args)
        except Exception as e:
            raise PipelineError(name, {"error": str(e)})
        steps.append({"step": name, "seconds": round(time.time() - start, 2)})
        if isinstance(result, dict) and "error" in result:
            raise PipelineError(name, result)
        return result

    parsed_job = run_step("parse_job", parse_job_description, safe_job)
    resume = run_step("write_resume", write_resume_content, safe_candidate, parsed_job)
    review = run_step("review_resume", review_resume, safe_candidate, parsed_job, resume)

    logger.info("pipeline finished: %s", steps)
    return {
        "parsed_job": parsed_job,
        "resume": resume,
        "review": review,
        "steps": steps,
    }