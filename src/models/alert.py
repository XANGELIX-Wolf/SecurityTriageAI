"""Alert data models."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class AlertSource(str, Enum):
    EDR = "edr"
    NETWORK = "network"
    CLOUD = "cloud"
    EMAIL = "email"
    IDENTITY = "identity"
    SIEM = "siem"


class SecurityAlert(BaseModel):
    id: str
    timestamp: datetime
    source: AlertSource
    title: str
    description: str
    severity_raw: str
    indicators: dict[str, Any] = Field(default_factory=dict)
    affected_asset: dict[str, str] = Field(default_factory=dict)
    raw_event: dict[str, Any] = Field(default_factory=dict)


class TriageResult(BaseModel):
    alert_id: str
    original_severity: str
    ai_severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    mitre_techniques: list[str] = Field(default_factory=list)
    kill_chain_phase: str
    reasoning: str
    recommended_actions: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    processing_time_ms: int = 0
    model_id: str = ""
