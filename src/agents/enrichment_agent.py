"""Enrichment Agent — Adds context to raw alerts before triage.

Enriches with:
- MITRE ATT&CK technique suggestions (LLM-assisted)
- Asset criticality context
- Historical correlation (simulated)

Provider-agnostic: uses whatever LLM is configured in .env
"""

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from src.llm.factory import get_llm

MITRE_FEW_SHOT = """\
Map this security alert to MITRE ATT&CK techniques.
Return a JSON array only. Each item: {{"technique_id": "T1059.001", "technique_name": "PowerShell", "confidence": 0.9}}

Examples:
- Alert: "PowerShell with encoded command from Word" → [{{"technique_id": "T1059.001", "technique_name": "PowerShell", "confidence": 0.95}}, {{"technique_id": "T1566.001", "technique_name": "Spearphishing Attachment", "confidence": 0.85}}]
- Alert: "Large outbound data transfer to unknown IP" → [{{"technique_id": "T1048", "technique_name": "Exfiltration Over Alternative Protocol", "confidence": 0.9}}]
- Alert: "47 failed logins then success from foreign IP" → [{{"technique_id": "T1110.001", "technique_name": "Password Guessing", "confidence": 0.95}}, {{"technique_id": "T1078", "technique_name": "Valid Accounts", "confidence": 0.8}}]

Alert to map:
{alert_summary}

JSON array only:"""


class EnrichmentAgent:
    """Enriches alerts with threat intel context before handing off to triage."""

    def __init__(self):
        self.llm = get_llm(temperature=0.0, max_tokens=512)
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", MITRE_FEW_SHOT),
        ])

    def enrich(self, alert: dict[str, Any]) -> dict[str, Any]:
        """Enrich an alert. Returns the alert with an 'enrichment' key added."""
        alert_summary = f"{alert.get('title', '')}. {alert.get('description', '')[:300]}"

        return {
            **alert,
            "enrichment": {
                "mitre_suggestions": self._suggest_mitre(alert_summary),
                "asset_context": self._get_asset_context(alert),
                "historical": self._correlate_history(alert),
            },
        }

    def _suggest_mitre(self, alert_summary: str) -> list[dict]:
        """Ask the LLM to suggest MITRE ATT&CK techniques for this alert."""
        try:
            response = self.llm.invoke(MITRE_FEW_SHOT.format(alert_summary=alert_summary))
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1].lstrip("json").strip()
            return json.loads(content)
        except Exception:
            return []

    def _get_asset_context(self, alert: dict) -> dict:
        """Extract and normalize asset context from the alert."""
        asset = alert.get("affected_asset", {})
        return {
            "hostname": asset.get("hostname", asset.get("user", "unknown")),
            "criticality": asset.get("criticality", "medium"),
            "department": asset.get("department", "unknown"),
            "environment": "production",
        }

    def _correlate_history(self, alert: dict) -> dict:
        """Simulate historical correlation. In production: query DynamoDB/Elasticsearch."""
        source = alert.get("source", "")
        # Simulate: identity/cloud alerts more likely to have related history
        related = {"identity": 3, "cloud": 2, "edr": 1, "network": 1, "email": 0}.get(source, 0)
        return {
            "similar_alerts_24h": related,
            "same_source_7d": related * 2,
            "known_false_positive": False,
        }
