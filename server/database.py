import json
import os
from pathlib import Path
from threading import Lock
from typing import Any
from dotenv import load_dotenv

load_dotenv()

_db_lock = Lock()
_default_db_path = Path(__file__).resolve().parent.parent / "database.json"
db_path = Path(os.getenv("DATABASE_JSON_PATH", str(_default_db_path))).resolve()

# Keep this symbol for compatibility with older imports.
engine = db_path


def _empty_db() -> dict[str, Any]:
    return {"users": [], "counters": {"users": 0}}


def _ensure_db_file() -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        db_path.write_text(json.dumps(_empty_db(), indent=2), encoding="utf-8")


def read_db() -> dict[str, Any]:
    with _db_lock:
        _ensure_db_file()
        try:
            data = json.loads(db_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = _empty_db()
            db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        data.setdefault("users", [])
        data.setdefault("counters", {})
        data["counters"].setdefault("users", 0)
        return data


def write_db(data: dict[str, Any]) -> None:
    with _db_lock:
        _ensure_db_file()
        temp_path = db_path.with_suffix(f"{db_path.suffix}.tmp")
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_path.replace(db_path)


def get_session():
    # Compatibility shim for older call sites that expect this function to exist.
    yield read_db()
