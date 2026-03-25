import os

from history.base import RunHistoryStore


def get_history_store() -> RunHistoryStore:
    backend = os.getenv("RUN_HISTORY_BACKEND", "file")

    if backend == "file":
        from history.file_store import FileRunHistoryStore
        return FileRunHistoryStore()

    if backend == "dynamodb":
        from history.dynamo_store import DynamoRunHistoryStore
        return DynamoRunHistoryStore()

    raise ValueError(f"Unknown RUN_HISTORY_BACKEND: {backend!r}")
