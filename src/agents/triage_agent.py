"""Triage Agent — ReAct agent for security alert severity assessment.

Uses whichever LLM provider is configured (Ollama/Groq/Bedrock).
Set LLM_PROVIDER in .env to switch providers with zero code changes.
"""

import json
import time
from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.llm.factory import get_llm
from src.tools.alert_enrichment import AlertEnrichmentTool
from src.tools.mitre_lookup import MitreLookupTool
from src.tools.severity_scorer import SeverityScorerTool


class TriageDecision(BaseModel):
    alert_id: str
    severity: str = Field(description="CRITICAL, HIGH, MEDIUM, LOW, or INFORMATIONAL")
    confidence: float = Field(ge=0.0, le=1.0)
    mitre_techniques: list[str] = Field(default_factory=list)
    kill_chain_phase: str
    reasoning: str
    recommended_actions: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    processing_time_ms: int = 0


TRIAGE_PROMPT = PromptTemplate.from_template("""\
You are an expert SOC analyst performing alert triage. Analyze the alert and determine severity.

Tools available:
{tools}

Tool names: {tool_names}

Instructions:
1. Use mitre_attack_lookup to identify relevant ATT&CK techniques
2. Use alert_enrichment to enrich key indicators (IPs, domains, hashes, users)
3. Use severity_scorer for a rule-based baseline score
4. Reason step-by-step: technique → kill chain phase → asset criticality → business impact
5. Produce a final triage decision

Alert:
{input}

Thinking:
{agent_scratchpad}
""")

EXTRACTION_PROMPT = """\
Extract a structured triage decision from this SOC analyst output.
Return ONLY valid JSON with these exact keys:
{{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFORMATIONAL",
  "confidence": 0.0-1.0,
  "mitre_techniques": ["T1059.001"],
  "kill_chain_phase": "exploitation",
  "reasoning": "one paragraph explanation",
  "recommended_actions": ["action 1", "action 2"],
  "escalation_required": true
}}

Alert ID: {alert_id}
Analysis to extract from:
{raw_output}

JSON only, no markdown:"""


class TriageAgent:
    """ReAct triage agent. Provider-agnostic via src/llm/factory.py"""

    def __init__(self):
        self.llm = get_llm(temperature=0.1, max_tokens=4096)
        self.extraction_llm = get_llm(temperature=0.0, max_tokens=1024)
        self.tools = [MitreLookupTool(), AlertEnrichmentTool(), SeverityScorerTool()]

        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=TRIAGE_PROMPT)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            max_iterations=6,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def triage(self, alert: dict[str, Any]) -> TriageDecision:
        """Triage a single alert. Returns a structured TriageDecision."""
        start = time.time()
        result = self.executor.invoke({"input": json.dumps(alert, indent=2)})
        decision = self._extract_decision(alert, result["output"])
        decision.processing_time_ms = int((time.time() - start) * 1000)
        return decision

    def _extract_decision(self, alert: dict, raw_output: str) -> TriageDecision:
        """Use a second LLM call to extract structured JSON from free-form agent output."""
        prompt = EXTRACTION_PROMPT.format(
            alert_id=alert.get("id", "unknown"),
            raw_output=raw_output,
        )
        response = self.extraction_llm.invoke(prompt)
        content = response.content.strip()

        # Strip markdown code fences if the model added them
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: return a safe default rather than crash
            data = {
                "severity": "MEDIUM",
                "confidence": 0.5,
                "mitre_techniques": [],
                "kill_chain_phase": "unknown",
                "reasoning": raw_output[:500],
                "recommended_actions": ["Manual review required"],
                "escalation_required": False,
            }

        data["alert_id"] = alert.get("id", "unknown")
        return TriageDecision(**data)
