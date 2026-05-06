"""Unit tests for data models."""

import pytest
from datetime import datetime
from src.models.alert import SecurityAlert, TriageResult, Severity, AlertSource


class TestSecurityAlert:
    def test_create_alert(self):
        alert = SecurityAlert(
            id="TEST-001", timestamp=datetime.now(), source=AlertSource.EDR,
            title="Test", description="Test", severity_raw="high",
        )
        assert alert.id == "TEST-001"


class TestTriageResult:
    def test_create_result(self):
        result = TriageResult(
            alert_id="TEST-001", original_severity="high", ai_severity=Severity.CRITICAL,
            confidence=0.92, mitre_techniques=["T1059.001"], kill_chain_phase="exploitation",
            reasoning="Encoded PowerShell from Word", recommended_actions=["Isolate host"],
            escalation_required=True,
        )
        assert result.escalation_required is True

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            TriageResult(
                alert_id="TEST", original_severity="low", ai_severity=Severity.LOW,
                confidence=1.5, kill_chain_phase="recon", reasoning="test",
            )
