"""Enrichment Agent - Gathers context to support triage decisions."""

import json
from typing import Any

from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate


class EnrichmentAgent:
    """Enriches raw alerts with MITRE mapping, asset context, and historical correlation."""

    def __init__(self, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        self.llm = ChatBedrock(
            model_id=model_id,
            model_kwargs={"temperature": 0.0, "max_tokens": 2048},
        )

    def enrich(self, alert: dict[str, Any]) -> dict[str, Any]:
        return {
            **alert,
            "enrichment": {
                "mitre_mapping": self._map_mitre_techniques(alert),
                "asset_context": self._get_asset_context(alert),
                "historical_correlation": self._correlate_history(alert),
            },
        }

    def _map_mitre_techniques(self, alert: dict) -> list[dict]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Map this security alert to MITRE ATT&CK techniques. Return a JSON list with 'technique_id', 'technique_name', and 'confidence' fields."),
            ("human", "{alert_data}"),
        ])
        response = (prompt | self.llm).invoke({"alert_data": str(alert)})
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return []

    def _get_asset_context(self, alert: dict) -> dict:
        # In production: query CMDB or asset inventory
        return {
            "asset_type": alert.get("affected_asset", {}).get("hostname", "unknown"),
            "criticality": alert.get("affected_asset", {}).get("criticality", "medium"),
            "environment": "production",
        }

    def _correlate_history(self, alert: dict) -> dict:
        # In production: query DynamoDB for related historical alerts
        return {"similar_alerts_24h": 0, "same_source_alerts_7d": 0, "known_false_positive": False}
