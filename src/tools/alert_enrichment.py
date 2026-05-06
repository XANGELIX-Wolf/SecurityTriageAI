"""Alert Enrichment Tool - Provides additional context for triage decisions."""

import json
from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class EnrichmentInput(BaseModel):
    indicator: str = Field(description="IP address, domain, hash, hostname, or user to enrich")
    indicator_type: str = Field(description="Type: ip, domain, hash, hostname, user")


class AlertEnrichmentTool(BaseTool):
    name: str = "alert_enrichment"
    description: str = (
        "Enrich an indicator (IP, domain, hash, hostname, or user) with "
        "threat intelligence, reputation, and historical context."
    )
    args_schema: Type[BaseModel] = EnrichmentInput

    def _run(self, indicator: str, indicator_type: str) -> str:
        return json.dumps(self._simulate_enrichment(indicator, indicator_type), indent=2)

    def _simulate_enrichment(self, indicator: str, indicator_type: str) -> dict:
        """Simulate threat intel enrichment. Production would call VirusTotal, AbuseIPDB, etc."""
        base = {"indicator": indicator, "type": indicator_type, "source": "synthetic_threat_intel"}
        if indicator_type == "ip":
            base.update({"reputation_score": 45, "geo": {"country": "RU", "asn": "AS12345"}, "known_malicious": False})
        elif indicator_type == "domain":
            base.update({"reputation_score": 30, "registered_date": "2024-11-01", "known_malicious": True, "threat_categories": ["phishing"]})
        elif indicator_type == "hash":
            base.update({"detection_ratio": "42/68", "malware_family": "Cobalt Strike", "known_malicious": True})
        elif indicator_type == "user":
            base.update({"account_type": "standard", "risk_score": 25, "recent_auth_failures": 3, "privileged": False})
        return base
