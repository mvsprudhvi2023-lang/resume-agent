import os

import pytest

# Test-only values. They are set before the app is imported,
# so the tests never touch your real key or passwords.
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["JWT_SECRET"] = "test-secret-for-pytest-only"
os.environ["ADMIN_PASSWORD"] = "test-admin-pass"
os.environ["USER_PASSWORD"] = "test-user-pass"


@pytest.fixture(autouse=True)
def isolate_audit_log(tmp_path, monkeypatch):
    import app.audit as audit_module

    monkeypatch.setattr(audit_module, "AUDIT_FILE", str(tmp_path / "audit.log"))