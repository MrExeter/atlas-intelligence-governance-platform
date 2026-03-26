import json
import os
from pathlib import Path

from history.base import RunHistoryStore


class FileRunHistoryStore(RunHistoryStore):
    """JSON file-based run history store for local development."""

    def __init__(self, path: str | None = None):
        self.path = Path(path or os.getenv("RUN_HISTORY_FILE", "data/run_history.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            with open(self.path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, records: list[dict]) -> None:
        content = json.dumps(records, indent=2)
        with open(self.path, "w") as f:
            f.write(content)

    def save_run(self, record: dict) -> None:
        records = self._load()
        records.append(record)
        self._save(records)

    def get_run(self, run_id: str) -> dict | None:
        for record in self._load():
            if record.get("run_id") == run_id:
                return record
        return None

    def list_runs(self, invite_token: str, limit: int = 20) -> list[dict]:
        records = [
            r for r in self._load()
            if r.get("invite_token") == invite_token and r.get("status") == "completed"
        ]
        records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return records[:limit]
