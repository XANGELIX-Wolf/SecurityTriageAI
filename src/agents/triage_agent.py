"""Triage Agent - Core ReAct reasoning agent for alert severity assessment."""

import json
from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src.tools.mitre_lookup import MitreLookupTool
from src.tools.alert_enrichment import AlertEnrichmentTool
from src.tools.severity_scorer import SeverityScorerTool


class TriageDecision(BaseModel):
    alert_id: str = Field(description="Original alert identifier")
    severity: str = Field(description="CRITICAL, HIGH, MEDIUM, LOW, or INFORMATIONAL")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    mitre_techniques: list[str] = Field(description="Mapped MITRE ATT&CK technique IDs")
    kill_chain_phase: str = Field(description="Estimated kill chain phase")
    reasoning: str = Field(description="Chain-of-thought explanation")
    recommended_actions: list[str] = Field(description="Suggested analyst actions")
    escalation_required: bool = Field(description="Whether immediate escalation is needed")


TRIAGE_PROMPT = PromptTemplate.from_template("""\
You are an expert SOC analyst performing alert triage.
Assess the severity and determine the appropriate response for the security alert below.

Available tools:
{tools}

Tool names: {tool_names}

Instructions:
1. Analyze the alert data
2. Use mitre_attack_lookup to identify relevant techniques
3. Use alert_enrichment for additional indicator context
4. Use severity_scorer for a rule-based baseline
5. Reason step-by-step about severity, kill chain phase, and business impact
6. Produce a structured triage decision

Alert Data:
{input}

{agent_scratchpad}
""")


class TriageAgent:
    """ReAct agent for security alert triage."""

    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.llm = ChatBedrock(
            model_id=model_id,
            model_kwargs={"temperature": 0.1, "max_tokens": 4096},
        )
        self.tools = [MitreLookupTool(), AlertEnrichmentTool(), SeverityScorerTool()]
        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=TRIAGE_PROMPT)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    def triage(self, alert: dict[str, Any]) -> TriageDecision:
        result = self.executor.invoke({"input": json.dumps(alert, indent=2)})
        return self._parse_decision(alert, result["output"])

    def _parse_decision(self, alert: dict, raw_output: str) -> TriageDecision:
        extraction_prompt = f"""Extract a structured triage decision from this SOC analyst output.
Alert ID: {alert.get('id', 'unknown')}
Analysis: {raw_output}

Return JSON with keys: severity, confidence, mitre_techniques, kill_chain_phase,
reasoning, recommended_actions, escalation_required"""
        response = self.llm.invoke(extraction_prompt)
        data = json.loads(response.content)
        data["alert_id"] = alert.get("id", "unknown")
        return TriageDecision(**data)
