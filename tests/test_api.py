from fastapi.testclient import TestClient

from app import agents
from app.main import app

client = TestClient(app)

ADMIN = ("admin", "test-admin-pass")
USER = ("analyst", "test-user-pass")
JOB = "We are hiring an AI Business Analyst with Python and SQL skills."


def login(username, password):
    return client.post("/login", data={"username": username, "password": password})


def headers_for(credentials):
    token = login(*credentials).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_is_public():
    assert client.get("/health").status_code == 200


def test_wrong_password_is_rejected():
    assert login("admin", "wrong-password").status_code == 401


def test_login_returns_token_and_role():
    response = login(*USER)
    assert response.status_code == 200
    assert response.json()["role"] == "user"


def test_no_token_is_blocked():
    assert client.get("/resumes").status_code == 401


def test_ai_endpoint_needs_login():
    response = client.post("/parse-job", json={"job_description": JOB})
    assert response.status_code == 401


def test_normal_user_cannot_list_resumes():
    assert client.get("/resumes", headers=headers_for(USER)).status_code == 403


def test_admin_can_list_resumes():
    assert client.get("/resumes", headers=headers_for(ADMIN)).status_code == 200


def test_bad_data_is_rejected():
    body = {
        "full_name": "Test Person",
        "email": "a@b.com",
        "job_description": JOB,
        "skills": ["Python"],
        "experience_years": 200,
    }
    response = client.post("/resumes", json=body, headers=headers_for(USER))
    assert response.status_code == 422


def test_write_resume_endpoint_is_removed():
    response = client.post("/write-resume", json={}, headers=headers_for(USER))
    assert response.status_code == 404


def test_parse_job_masks_pii(monkeypatch):
    prompts = []

    def fake_llm(prompt):
        prompts.append(prompt)
        return '{"job_title": "x", "required_skills": [], "nice_to_have_skills": [], "keywords": []}'

    monkeypatch.setattr(agents, "ask_llm", fake_llm)
    body = {"job_description": JOB + " Send your CV to hr@example.com."}
    response = client.post("/parse-job", json=body, headers=headers_for(USER))
    assert response.status_code == 200
    assert "hr@example.com" not in prompts[0]