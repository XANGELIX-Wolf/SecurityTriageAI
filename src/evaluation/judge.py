"""LLM-as-Judge - Evaluates triage quality across 5 dimensions.

Dimensions scored 0-10:
1. Severity Accuracy
2. ATT&CK Mapping
3. Reasoning Quality
4. Actionability
5. Completeness
"""

import json
from pathlib import Path
from typing import Any

from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
    alert_id: str
    severity_accuracy: float = Field(ge=0, le=10)
    attack_mapping: float = Field(ge=0, le=10)
    reasoning_quality: float = Field(ge=0, le=10)
    actionability: float = Field(ge=0, le=10)
    completeness: float = Field(ge=0, le=10)
    overall: float = Field(ge=0, le=10)
    feedback: str = ""


JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert SOC manager evaluating AI-generated alert triage decisions.

Score each dimension 0-10:
- severity_accuracy: Does severity match expert judgment?
- attack_mapping: Are MITRE techniques correctly identified?
- reasoning_quality: Is the reasoning logical and evidence-based?
- actionability: Are recommended actions specific and prioritized?
- completeness: Are all indicators and context addressed?

Return JSON: {{"severity_accuracy": N, "attack_mapping": N, "reasoning_quality": N, "actionability": N, "completeness": N, "overall": N, "feedback": "..."}}""" ),
    ("human", """## Original Alert\n{alert}\n\n## Triage Decision\n{triage_result}\n\n## Expert Baseline\n{baseline}\n\nProvide evaluation scores as JSON."""),
])


class TriageJudge:
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.llm = ChatBedrock(model_id=model_id, model_kwargs={"temperature": 0.0, "max_tokens": 1024})
        self.chain = JUDGE_PROMPT | self.llm

    def evaluate_single(self, alert: dict, triage_result: dict, baseline: dict | None = None) -> EvaluationScore:
        response = self.chain.invoke({
            "alert": json.dumps(alert, indent=2),
            "triage_result": json.dumps(triage_result, indent=2),
            "baseline": json.dumps(baseline, indent=2) if baseline else "No expert baseline available.",
        })
        scores = json.loads(response.content)
        scores["alert_id"] = alert.get("id", "unknown")
        return EvaluationScore(**scores)


def evaluate_results(results: list[dict], baselines_path: Path | None = None) -> dict[str, Any]:
    judge = TriageJudge()
    baselines = {}
    if baselines_path and baselines_path.exists():
        with open(baselines_path) as f:
            baselines = {b["alert_id"]: b for b in json.load(f)}

    scores = []
    for result in results:
        score = judge.evaluate_single(
            alert=result.get("original_alert", {}),
            triage_result=result,
            baseline=baselines.get(result.get("alert_id", "")),
        )
        scores.append(score.model_dump())

    avg = sum(s["overall"] for s in scores) / len(scores) if scores else 0
    return {
        "scores": scores, "average": round(avg, 2), "count": len(scores),
        "dimensions": {d: round(sum(s[d] for s in scores) / len(scores), 2) for d in ["severity_accuracy", "attack_mapping", "reasoning_quality", "actionability", "completeness"]} if scores else {},
    }
