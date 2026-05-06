"""Triage Pipeline Orchestrator.

Coordinates: alert normalization → enrichment → triage → results.
Supports both real LLM and mock mode (--mock flag or MOCK=true env var).
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Any

import structlog

from src.agents.enrichment_agent import EnrichmentAgent
from src.agents.triage_agent import TriageAgent
from src.pipeline.mock import MOCK_DECISIONS

logger = structlog.get_logger()

ALERT_TIMEOUT_SECONDS = 60


class TriagePipeline:
    """Orchestrates the full triage workflow."""

    def __init__(self, mock: bool = False):
        self.mock = mock or os.getenv("MOCK", "").lower() == "true"
        if not self.mock:
            self.enrichment_agent = EnrichmentAgent()
            self.triage_agent = TriageAgent()

    def run(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process alerts. Uses ThreadPoolExecutor for concurrent processing."""
        if self.mock:
            return self._run_mock(alerts)
        return self._run_live(alerts)

    def _run_live(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self._process_one, alert): alert for alert in alerts}
            for future in as_completed(futures, timeout=ALERT_TIMEOUT_SECONDS * len(alerts)):
                alert = futures[future]
                try:
                    results.append(future.result(timeout=ALERT_TIMEOUT_SECONDS))
                except TimeoutError:
                    logger.error("alert_timeout", alert_id=alert.get("id"))
                    results.append(_error_result(alert, "Triage timed out"))
                except Exception as e:
                    logger.error("triage_failed", alert_id=alert.get("id"), error=str(e))
                    results.append(_error_result(alert, str(e)))
        return results

    def _process_one(self, alert: dict[str, Any]) -> dict[str, Any]:
        logger.info("processing", alert_id=alert.get("id"))
        enriched = self.enrichment_agent.enrich(alert)
        decision = self.triage_agent.triage(enriched)
        return {
            "original_alert": alert,
            "enrichment": enriched.get("enrichment", {}),
            **decision.model_dump(),
        }

    def _run_mock(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return pre-built mock decisions — zero API calls, zero cost."""
        results = []
        for alert in alerts:
            mock = MOCK_DECISIONS.get(alert["id"], _default_mock(alert))
            results.append({"original_alert": alert, **mock})
            time.sleep(0.3)  # Simulate processing time in demo
        return results


def _error_result(alert: dict, error: str) -> dict:
    return {"original_alert": alert, "alert_id": alert.get("id", "unknown"), "error": error, "severity": "UNKNOWN", "escalation_required": False}


def _default_mock(alert: dict) -> dict:
    return {
        "alert_id": alert["id"],
        "severity": "MEDIUM",
        "confidence": 0.7,
        "mitre_techniques": [],
        "kill_chain_phase": "unknown",
        "reasoning": "Mock triage — no matching decision found.",
        "recommended_actions": ["Manual review"],
        "escalation_required": False,
        "processing_time_ms": 300,
    }
