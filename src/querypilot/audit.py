import json
import threading
import time

from .config import settings

_lock = threading.Lock()


def log(tool: str, detail: str, status: str, elapsed_ms: float = 0.0) -> None:
    """Append an event to the JSONL audit log.

    Guarantees no database passwords, connection URLs, or result rows are ever written.
    """
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "tool": tool,
        "detail": (detail or "")[:2000],  # query or identifier only, never rows, never secrets
        "status": status,  # ok | blocked | timeout | error
        "elapsed_ms": elapsed_ms,
    }
    with _lock, open(settings.audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
