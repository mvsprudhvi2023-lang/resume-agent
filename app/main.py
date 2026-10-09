from fastapi import FastAPI, HTTPException
from app.models import ResumeRequest, ResumeResponse, ParseRequest
from app.agents import parse_job_description

app = FastAPI(title="Enterprise AI Resume Generator")

# Temporary storage in memory (resets when the server restarts)
resumes = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/resumes", response_model=ResumeResponse)
def create_resume(request: ResumeRequest):
    new_id = len(resumes) + 1
    resumes.append({"id": new_id, **request.model_dump()})
    return ResumeResponse(
        id=new_id,
        full_name=request.full_name,
        status="received",
        message="Request saved. AI generation comes on Day 3.",
    )


@app.get("/resumes")
def list_resumes():
    return resumes


@app.get("/resumes/{resume_id}")
def get_resume(resume_id: int):
    for item in resumes:
        if item["id"] == resume_id:
            return item
    raise HTTPException(status_code=404, detail="Resume not found")



@app.post("/parse-job")
def parse_job(request: ParseRequest):
    try:
        return parse_job_description(request.job_description)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")