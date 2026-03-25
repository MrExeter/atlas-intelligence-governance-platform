import os

import boto3
from boto3.dynamodb.conditions import Key

from history.base import RunHistoryStore


class DynamoRunHistoryStore(RunHistoryStore):
    """DynamoDB-backed run history store for production."""

    def __init__(self, table_name: str | None = None, region: str | None = None):
        table_name = table_name or os.getenv("RUN_HISTORY_TABLE", "atlas_run_history")
        region = region or os.getenv("AWS_REGION", "us-west-1")
        self._table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    def save_run(self, record: dict) -> None:
        item = dict(record)
        # SK is timestamp#run_id for time-sortable queries
        item["sk"] = f"{record['timestamp']}#{record['run_id']}"
        item["pk"] = record["invite_token"]
        self._table.put_item(Item=item)

    def get_run(self, run_id: str) -> dict | None:
        # Scan with filter — acceptable at demo scale.
        # Add a GSI on run_id for production-scale lookups.
        response = self._table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("run_id").eq(run_id),
            Limit=1,
        )
        items = response.get("Items", [])
        return items[0] if items else None

    def list_runs(self, invite_token: str, limit: int = 20) -> list[dict]:
        response = self._table.query(
            KeyConditionExpression=Key("pk").eq(invite_token),
            ScanIndexForward=False,  # newest first (descending SK)
            Limit=limit,
        )
        return response.get("Items", [])
