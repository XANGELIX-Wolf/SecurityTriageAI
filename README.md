# SecurityTriageAI

> **From noise to signal: An agentic approach to security alert triage**

An autonomous AI agent that ingests raw security alerts, enriches them with threat intelligence and MITRE ATT&CK context, performs multi-step reasoning to assess severity and urgency, and produces analyst-ready triage reports — complete with an LLM-as-judge quality evaluation framework.

---

## 🎯 What This Demonstrates

| Capability | Implementation |
|---|---|
| **Agentic AI Workflows** | Multi-step ReAct agent with tool use, memory, and planning |
| **LLM Integration** | AWS Bedrock (Claude) with structured prompts and chain-of-thought |
| **Security Domain Expertise** | MITRE ATT&CK mapping, kill-chain analysis, SOC workflow alignment |
| **Quality Evaluation** | LLM-as-judge scoring, precision/recall metrics, regression testing |
| **Cloud-Native Architecture** | AWS Bedrock + Lambda + Step Functions + DynamoDB |
| **Production Readiness** | CI/CD, IaC (CDK), observability, cost controls |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  ALERT INGESTION                            │
│              (EventBridge / SQS Queue)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER                            │
│           (AWS Step Functions)                              │
│                                                             │
│  ┌─────────┐    ┌──────────┐    ┌───────────────────────┐  │
│  │ Enrich  │───▶│  Triage  │───▶│  Report & Route       │  │
│  │  Agent  │    │  Agent   │    │     Agent             │  │
│  └─────────┘    └──────────┘    └───────────────────────┘  │
│       │              │                    │                 │
│       ▼              ▼                    ▼                 │
│  ┌─────────┐    ┌──────────┐    ┌───────────────────────┐  │
│  │  MITRE  │    │ Bedrock  │    │    DynamoDB           │  │
│  │ ATT&CK  │    │ (Claude) │    │   (Results)           │  │
│  └─────────┘    └──────────┘    └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              EVALUATION LAYER                               │
│         (LLM-as-Judge Quality Scoring)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI configured with Bedrock access
- Node.js 18+ (for CDK)

### Setup
```bash
git clone https://github.com/XANGELIX-Wolf/SecurityTriageAI.git
cd SecurityTriageAI
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main --input data/sample_alerts.json
```

### Run Evaluation
```bash
python -m src.evaluation.judge --results output/triage_results.json
```

---

## 📁 Project Structure

```
SecurityTriageAI/
├── src/
│   ├── agents/          # LangChain agent definitions
│   ├── tools/           # Agent tools (MITRE, enrichment, scoring)
│   ├── models/          # Data models and schemas
│   ├── evaluation/      # LLM-as-judge framework
│   ├── pipeline/        # Orchestration logic
│   └── main.py          # Entry point
├── data/
│   ├── sample_alerts.json
│   └── baselines/       # Expert triage baselines for eval
├── infra/               # AWS CDK stacks
├── tests/               # Unit and integration tests
├── docs/                # Architecture decisions
└── .github/workflows/   # CI/CD pipeline
```

---

## 🧪 Evaluation Framework

The LLM-as-judge evaluates triage quality across 5 dimensions:
1. **Severity Accuracy** — Does the assigned severity match expert consensus?
2. **ATT&CK Mapping** — Are techniques correctly identified?
3. **Reasoning Quality** — Is the chain-of-thought logical and complete?
4. **Actionability** — Are recommended actions specific and relevant?
5. **Completeness** — Are all relevant indicators addressed?

---

## 📜 Disclaimer

*This is an independent personal portfolio project. It uses no proprietary data, tools, or intellectual property from any employer. All alert data is synthetic. All code is original.*

---

## 📄 License

MIT
