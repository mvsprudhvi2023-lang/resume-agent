import json
import logging
import os
from datetime import datetime, timezone

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("resume_agent")

AUDIT_FILE = "logs/audit.log"


def audit(user: dict, action: str, **details):
    record = {
        "time": datetime.now(timezone.utc).isoformat(),
        "user": user.get("username"),
        "role": user.get("role"),
        "action": action,
        **details,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    logger.info("audit: %s by %s", action, user.get("username"))