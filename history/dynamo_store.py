import json
import os
from decimal import Decimal

import boto3

from history.base import RunHistoryStore


def _to_decimal(record: dict) -> dict:
    """Convert all floats to Decimal for DynamoDB compatibility."""
    return json.loads(json.dumps(record), parse_float=Decimal)


def _from_decimal(record: dict) -> dict:
    """Convert Decimal values back to float for JSON serialization."""
    def _default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    return json.loads(json.dumps(record, default=_default))


class DynamoRunHistoryStore(RunHistoryStore):
    """DynamoDB-backed run history store for production."""

    def __init__(self, table_name: str | None = None, region: str | None = None):
        table_name = table_name or os.getenv("RUN_HISTORY_TABLE", "atlas_run_history")
        region = region or os.getenv("AWS_REGION", "us-west-1")
        self._table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    def save_run(self, record: dict) -> None:
        self._table.put_item(Item=_to_decimal(record))

    def get_run(self, run_id: str) -> dict | None:
        response = self._table.get_item(Key={"run_id": run_id})
        item = response.get("Item")
        return _from_decimal(item) if item else None

    def list_runs(self, invite_token: str, limit: int = 20) -> list[dict]:
        # Table PK is run_id — scan and filter by invite_token.
        # Acceptable at demo scale; add a GSI on invite_token for production scale.
        response = self._table.scan(
            FilterExpression=(
                boto3.dynamodb.conditions.Attr("invite_token").eq(invite_token) &
                boto3.dynamodb.conditions.Attr("status").eq("completed")
            )
        )
        items = [_from_decimal(item) for item in response.get("Items", [])]
        items.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return items[:limit]
