import logging
import os

from history.base import RunHistoryStore

logger = logging.getLogger("atlas")


def get_history_store() -> RunHistoryStore:
    backend = os.getenv("RUN_HISTORY_BACKEND", "file")

    if backend == "file":
        from history.file_store import FileRunHistoryStore
        logger.info("RunHistoryStore: using FileRunHistoryStore")
        return FileRunHistoryStore()

    if backend == "dynamodb":
        from history.dynamo_store import DynamoRunHistoryStore
        logger.info("RunHistoryStore: using DynamoRunHistoryStore (table=%s)",
                    os.getenv("RUN_HISTORY_TABLE", "atlas_run_history"))
        return DynamoRunHistoryStore()

    raise ValueError(f"Unknown RUN_HISTORY_BACKEND: {backend!r}")
