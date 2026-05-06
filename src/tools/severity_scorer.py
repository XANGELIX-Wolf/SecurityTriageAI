"""Severity Scorer Tool - Rule-based severity assessment baseline."""

import json
from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class SeverityInput(BaseModel):
    alert_type: str = Field(description="Type of alert: malware, brute_force, exfiltration, phishing, etc.")
    asset_criticality: str = Field(description="Asset criticality: critical, high, medium, low")
    confidence: float = Field(description="Detection confidence 0.0-1.0")
    kill_chain_phase: str = Field(description="Kill chain phase: recon, delivery, exploitation, installation, c2, actions_on_objectives")


class SeverityScorerTool(BaseTool):
    name: str = "severity_scorer"
    description: str = (
        "Calculate a rule-based severity baseline. Combine with contextual analysis for final determination."
    )
    args_schema: Type[BaseModel] = SeverityInput

    PHASE_SCORES = {"recon": 1, "delivery": 2, "exploitation": 4, "installation": 5, "c2": 6, "command_and_control": 6, "actions_on_objectives": 8}
    CRITICALITY_MULTIPLIER = {"critical": 2.0, "high": 1.5, "medium": 1.0, "low": 0.5}
    ALERT_TYPE_SCORES = {"malware": 7, "ransomware": 10, "exfiltration": 9, "brute_force": 4, "phishing": 5, "lateral_movement": 7, "privilege_escalation": 8, "c2_beacon": 8, "policy_violation": 2, "anomaly": 3}

    def _run(self, alert_type: str, asset_criticality: str, confidence: float, kill_chain_phase: str) -> str:
        type_score = self.ALERT_TYPE_SCORES.get(alert_type.lower(), 3)
        phase_score = self.PHASE_SCORES.get(kill_chain_phase.lower(), 2)
        multiplier = self.CRITICALITY_MULTIPLIER.get(asset_criticality.lower(), 1.0)
        raw_score = (type_score + phase_score) * multiplier * confidence
        normalized = min(raw_score / 36.0 * 10, 10)
        severity = "CRITICAL" if normalized >= 8 else "HIGH" if normalized >= 6 else "MEDIUM" if normalized >= 4 else "LOW" if normalized >= 2 else "INFORMATIONAL"
        return json.dumps({"normalized_score": round(normalized, 2), "severity": severity, "factors": {"type": type_score, "phase": phase_score, "criticality_mult": multiplier, "confidence": confidence}}, indent=2)
