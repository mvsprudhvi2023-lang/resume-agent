from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.agents import parse_job_description
from app.audit import audit
from app.auth import authenticate, create_token, get_current_user, require_admin
from app.models import ParseRequest, ResumeRequest, ResumeResponse, WriteRequest
from app.orchestrator import PipelineError, run_pipeline
from app.privacy import mask_pii

app = FastAPI(title="Enterprise AI Resume Generator")

# Temporary storage in memory (resets when the server restarts)
resumes = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form.username, form.password)
    if not user:
        audit({"username": mask_pii(form.username), "role": None}, "login_failed")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    audit(user, "login_success")
    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "role": user["role"],
    }


@app.post("/resumes", response_model=ResumeResponse)
def create_resume(request: ResumeRequest, user: dict = Depends(get_current_user)):
    new_id = len(resumes) + 1
    resumes.append({"id": new_id, **request.model_dump()})
    audit(user, "create_resume", resume_id=new_id)
    return ResumeResponse(
        id=new_id,
        full_name=request.full_name,
        status="received",
        message="Request saved.",
    )


@app.get("/resumes")
def list_resumes(admin: dict = Depends(require_admin)):
    audit(admin, "list_resumes", count=len(resumes))
    return resumes


@app.get("/resumes/{resume_id}")
def get_resume(resume_id: int, admin: dict = Depends(require_admin)):
    audit(admin, "view_resume", resume_id=resume_id)
    for item in resumes:
        if item["id"] == resume_id:
            return item
    raise HTTPException(status_code=404, detail="Resume not found")


@app.post("/parse-job")
def parse_job(request: ParseRequest, user: dict = Depends(get_current_user)):
    audit(user, "parse_job")
    try:
        return parse_job_description(mask_pii(request.job_description))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")


@app.post("/generate-resume")
def generate_resume(request: WriteRequest, user: dict = Depends(get_current_user)):
    candidate = {
        "full_name": request.full_name,
        "skills": request.skills,
        "experience_years": request.experience_years,
        "achievements": request.achievements,
    }
    try:
        result = run_pipeline(candidate, request.job_description)
    except PipelineError as e:
        audit(user, "generate_resume_failed", failed_step=e.step)
        raise HTTPException(
            status_code=502,
            detail={"failed_step": e.step, "result": e.detail},
        )
    except Exception as e:
        audit(user, "generate_resume_failed", failed_step="unknown")
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    audit(
        user,
        "generate_resume",
        ats_score=result["review"].get("ats_score"),
        seconds=round(sum(s["seconds"] for s in result["steps"]), 2),
    )
    return result