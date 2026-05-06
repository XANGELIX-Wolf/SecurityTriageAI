# 🛡️ Agentic AI for Security Triage

> **A free, hands-on curriculum for security practitioners learning to build AI systems**

Built by a security practitioner with 5 years of SOC operations experience, this project teaches you to build a **production-grade agentic AI alert triage system** from scratch — at **zero cost** — using open-source LLMs and free API tiers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LLM: Ollama | Groq | Bedrock](https://img.shields.io/badge/LLM-Ollama%20%7C%20Groq%20%7C%20Bedrock-green)](SETUP.md)

---

## 🎓 What You'll Learn

By the end of this curriculum, you will know how to:

- ✅ Implement a **ReAct (Reason + Act) agent** that thinks step-by-step before acting
- ✅ Enrich security alerts with **MITRE ATT&CK context** automatically
- ✅ Build a **multi-agent pipeline** with concurrent execution
- ✅ Evaluate AI output quality using the **LLM-as-judge** pattern
- ✅ Wire this to **AWS Bedrock, Groq, or a local LLM** — interchangeably
- ✅ Run the whole thing **free** during development and learning

---

## 👥 Who This Is For

| Background | Value |
|---|---|
| **SOC Analysts / Security Engineers** | Understand how AI can augment your workflow — and build it yourself |
| **Security Students / Bootcamp Grads** | A real-world AI project you can explain in interviews |
| **Software Engineers entering Security AI** | Domain-grounded LLM integration patterns |
| **Anyone on a $0 cloud budget** | Everything in the core curriculum runs for free |

---

## 📚 Curriculum

| Module | Notebook | Topic |
|---|---|---|
| **00** | [Introduction](notebooks/00_introduction.ipynb) | What is agentic AI? Why for security? The problem with rule-based triage |
| **01** | [ReAct Agents](notebooks/01_react_agent.ipynb) | Think → Act → Observe: building a reasoning agent step by step |
| **02** | [LLM Providers](notebooks/02_llm_providers.ipynb) | Run for free: mock → Ollama → Groq → Bedrock (same code, different config) |
| **03** | [Evaluation](notebooks/03_evaluation.ipynb) | LLM-as-judge: teaching AI to grade its own triage decisions |

> 📖 See [CURRICULUM.md](CURRICULUM.md) for detailed learning objectives, prerequisites, and exercises per module.

---

## ⚡ Quick Start (Free — 3 Commands)

```bash
git clone https://github.com/XANGELIX-Wolf/SecurityTriageAI.git
cd SecurityTriageAI
pip install -r requirements.txt
python demo.py
```

You'll see a rich terminal UI triaging 5 realistic synthetic security alerts — severity scoring, MITRE mapping, analyst recommendations, and evaluation scores. **No API key. No cloud account. No cost.**

**Ready for a real LLM (still free):**

```bash
# Option A: Ollama — runs locally on your Mac/PC, free forever
brew install ollama && ollama pull llama3.1
LLM_PROVIDER=ollama python demo.py --live

# Option B: Groq — free cloud API, no credit card required
# Get key at: console.groq.com
GROQ_API_KEY=your_key LLM_PROVIDER=groq python demo.py --live
```

See [SETUP.md](SETUP.md) for full provider setup including AWS Bedrock.

---

## 🏗️ System Architecture

A **multi-agent pipeline** — a core pattern in modern AI engineering:

```
Raw Security Alert
       |
       v
+------------------+    +------------------+    +------------------+
|  ENRICHMENT      |--->|  TRIAGE          |--->|  EVALUATION      |
|  AGENT           |    |  AGENT           |    |  (LLM Judge)     |
|                  |    |                  |    |                  |
|  * MITRE lookup  |    |  ReAct loop:     |    |  Scores across   |
|  * IOC context   |    |  Think > Act     |    |  5 dimensions    |
|  * Kill chain    |    |  > Observe       |    |  vs. baselines   |
+------------------+    +------------------+    +------------------+
         |                       |                       |
         +-----------------------+-----------------------+
                                 |
                        LLM Provider Layer
                   (swap via .env -- no code changes)
              Ollama (free) | Groq (free) | Bedrock (pay-per-token)
```

> 📖 See [LEARN.md](LEARN.md) for a deep-dive on *why* each architectural decision was made.

---

## 💡 Key Design Decisions

**Why ReAct instead of a simple prompt?**
Chain-of-thought prompts break on novel inputs. ReAct agents use tools mid-reasoning — dynamically querying MITRE, checking IOC context, and course-correcting. This produces grounded, explainable triage decisions.

**Why MITRE ATT&CK as the enrichment ontology?**
Every security tool speaks MITRE. Output mapped to ATT&CK techniques is immediately actionable in any SOC environment. It's also behavioral, not signature-based — future-proof against new malware.

**Why LLM-as-judge for evaluation?**
Judging quality is easier than generating quality. A smaller, cheaper model can reliably evaluate a larger model's triage decisions against a rubric — scaling expert review without expert cost.

**Why provider-agnostic architecture?**
AWS Bedrock costs money during development. By abstracting the LLM behind a factory pattern (`src/llm/factory.py`), you develop with free local models and switch to production providers with one environment variable.

---

## 📁 Project Structure

```
SecurityTriageAI/
├── notebooks/               <- Start here if you're learning
│   ├── 00_introduction.ipynb
│   ├── 01_react_agent.ipynb
│   ├── 02_llm_providers.ipynb
│   └── 03_evaluation.ipynb
├── src/
│   ├── agents/              <- Enrichment and triage agent implementations
│   ├── llm/                 <- Provider-agnostic LLM factory
│   ├── pipeline/            <- Orchestrator + mock mode
│   ├── tools/               <- MITRE, enrichment, scoring tools
│   ├── models/              <- Pydantic data models (alerts, decisions)
│   └── evaluation/          <- LLM-as-judge framework
├── data/
│   ├── sample_alerts.json   <- 5 realistic synthetic security alerts
│   └── baselines/           <- Expert triage decisions for evaluation
├── demo.py                  <- Run the demo (mock or live LLM)
├── CURRICULUM.md            <- Detailed syllabus with exercises
├── LEARN.md                 <- Architecture decisions explained
├── SETUP.md                 <- Provider setup (Ollama, Groq, Bedrock)
└── .env.example             <- Configuration template
```

---

## 🧑‍🏫 About This Project

This project was built by a security practitioner who has spent years watching smart people struggle with the same challenge: **you need expert-level judgment at machine speed**.

It's structured as a curriculum rather than just a codebase because reading code without context teaches syntax. Building with explained intent teaches you to *think* like an AI engineer.

The "free" constraint is intentional. Security teams often can't spin up cloud AI without budget approval. This curriculum proves you don't need to — you can learn the entire stack locally, then plug in a cloud provider when it counts.

---

## 📜 Disclaimer

*This is an independent personal project. All alert data is synthetic. No proprietary data, tools, or intellectual property from any employer is used. All code is original.*

---

## 📄 License

MIT — Use it, fork it, teach it.
