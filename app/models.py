from typing import List
from pydantic import BaseModel, Field


class ResumeRequest(BaseModel):
    full_name: str = Field(min_length=2)
    email: str
    job_description: str = Field(min_length=20)
    skills: List[str]
    experience_years: int = Field(ge=0, le=60)


class ResumeResponse(BaseModel):
    id: int
    full_name: str
    status: str
    message: str



class ParseRequest(BaseModel):
    job_description: str = Field(min_length=20)



class WriteRequest(BaseModel):
    full_name: str = Field(min_length=2)
    job_description: str = Field(min_length=20)
    skills: List[str]
    experience_years: int = Field(ge=0, le=60)
    achievements: List[str] = []