import time
from app.agents import parse_job_description, write_resume_content, review_resume


class PipelineError(Exception):
    def __init__(self, step: str, detail: dict):
        self.step = step
        self.detail = detail
        super().__init__(f"Step '{step}' failed")


def run_pipeline(candidate: dict, job_description: str) -> dict:
    steps = []
    
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

    parsed_job = run_step("parse_job", parse_job_description, job_description)
    resume = run_step("write_resume", write_resume_content, candidate, parsed_job)
    review = run_step("review_resume", review_resume, candidate, parsed_job, resume)

    return {
        "parsed_job": parsed_job,
        "resume": resume,
        "review": review,
        "steps": steps,
    }