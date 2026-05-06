"""Triage Pipeline Orchestrator - Coordinates enrichment → triage → output."""

import time
from typing import Any

import structlog

from src.agents.enrichment_agent import EnrichmentAgent
from src.agents.triage_agent import TriageAgent

logger = structlog.get_logger()


class TriagePipeline:
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.enrichment_agent = EnrichmentAgent()
        self.triage_agent = TriageAgent(model_id=model_id)

    def run(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for i, alert in enumerate(alerts):
            logger.info("processing_alert", index=i + 1, total=len(alerts), alert_id=alert.get("id"))
            start = time.time()
            try:
                enriched = self.enrichment_agent.enrich(alert)
                decision = self.triage_agent.triage(enriched)
                results.append({
                    "original_alert": alert,
                    "enrichment": enriched.get("enrichment", {}),
                    **decision.model_dump(),
                    "processing_time_ms": int((time.time() - start) * 1000),
                })
                logger.info("alert_triaged", alert_id=alert.get("id"), severity=decision.severity)
            except Exception as e:
                logger.error("triage_failed", alert_id=alert.get("id"), error=str(e))
                results.append({"original_alert": alert, "alert_id": alert.get("id", "unknown"), "error": str(e), "severity": "UNKNOWN"})
        return results
