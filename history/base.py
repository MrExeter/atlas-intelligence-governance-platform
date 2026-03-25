from abc import ABC, abstractmethod


class RunHistoryStore(ABC):
    """Abstract interface for run history storage backends."""

    @abstractmethod
    def save_run(self, record: dict) -> None:
        """Persist a completed run record."""
        ...

    @abstractmethod
    def get_run(self, run_id: str) -> dict | None:
        """Retrieve a single run by run_id. Returns None if not found."""
        ...

    @abstractmethod
    def list_runs(self, invite_token: str, limit: int = 20) -> list[dict]:
        """Return the most recent runs for an invite token, newest first."""
        ...
