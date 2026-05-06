# LEARN.md — Architectural Decisions Explained

Every architectural choice in this project was deliberate. This document explains the **why** behind each major decision — the reasoning that goes into designing a production AI system, not just the implementation.

---

## 1. Why ReAct Instead of a Simple Prompt Chain?

**The naive approach:**
```python
response = llm.invoke(f"Triage this security alert: {alert_text}")
```

This works surprisingly well for textbook alerts. The cracks appear at the edges:
- Alert mentions a process name you haven't seen (`svchost.exe` launching `cmd.exe` — normal or not?)
- Alert involves an external IP that needs context
- Alert requires correlating behavior against a known kill-chain stage

A simple prompt can only use what's in the context window. You either stuff everything in upfront (expensive, slow, noisy) or the LLM hallucinates.

**ReAct's key insight:** Deciding *what to look up* is much easier than knowing everything upfront. Let the LLM decide what it needs, fetch it, and continue reasoning.

```
Thought: "This looks like credential dumping. Let me verify the MITRE technique."
Action:  mitre_lookup(query="lsass memory dump credential access")
Observation: "T1003.001 -- LSASS Memory. Tactic: Credential Access. Kill chain: Exploitation."
Thought: "Confirmed T1003.001. Combined with the earlier persistence indicator, escalating."
Final Answer: {severity: "CRITICAL", techniques: ["T1003.001"], ...}
```

The result is grounded, explainable, and traceable — a security analyst can audit every step.

---

## 2. Why MITRE ATT&CK as the Enrichment Ontology?

We could have used: NIST controls, OWASP Top 10, CVE database, or the Lockheed Martin Kill Chain.

MITRE ATT&CK wins because:

**Universal vocabulary.** Every major security product (CrowdStrike, Sentinel, Splunk, QRadar) maps to MITRE. AI output that speaks ATT&CK is immediately usable in any SOC environment, with any tooling.

**Behavioral, not signature-based.** MITRE describes *what adversaries do*, not *what their malware looks like*. A new ransomware variant encrypts files — that's still T1486. MITRE is future-proof in a way that signature databases are not.

**Structured hierarchy.** Tactics > Techniques > Sub-techniques gives the LLM a decision tree to navigate. "Which tactic does this behavior fall under?" is a much better-constrained question than "Is this malicious?"

**Hidden benefit:** Forcing yourself (and your AI) to map every alert to ATT&CK improves your own analytical reasoning. This project is professional development for the builder as much as the learner.

---

## 3. Why LLM-as-Judge for Evaluation?

**The problem with traditional metrics:**
Accuracy requires ground truth labels. Getting security analysts to label thousands of triage decisions is expensive and slow. Even then, experts disagree ~15-20% of the time.

**The problem with human review at scale:**
You can't manually review every AI output. You need automation that tells you *which* outputs warrant human review — and why.

**LLM-as-judge works because:**

*Judging is easier than generating.* An LLM that can't reliably produce a perfect triage decision can still reliably tell you whether a triage decision has inconsistent reasoning, missing indicators, or non-actionable recommendations. The evaluation task is fundamentally simpler.

*Rubric-based scoring is consistent.* A 5-dimension rubric applied uniformly is more valuable than inconsistent ad-hoc human review. Consistency enables comparison across time, models, and prompt changes.

*Cost separation.* Use a small, cheap model as judge (Claude Haiku, Llama 3.1 8B). Use a larger model for generation. The judge doesn't need to be smart — it needs to be consistent.

**The key design principle:** Define your evaluation rubric *before* you build your system. The rubric is your specification. Build toward it.

---

## 4. Why Provider-Agnostic Architecture?

```python
# src/llm/factory.py -- the entire LLM decision in ~20 lines
def get_llm(provider=None):
    provider = provider or os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":    return ChatOllama(...)
    elif provider == "groq":    return ChatGroq(...)
    elif provider == "bedrock": return ChatBedrock(...)
```

Three reasons to abstract this:

**Development velocity.** You can't iterate efficiently when every test costs money. Mock mode and Ollama let you run 100 experiments for $0.

**Interview and collaboration flexibility.** "We use Azure OpenAI" -> "Here's how I'd add that provider." The factory pattern demonstrates architectural thinking — you're not just a user of one tool.

**Career longevity.** The specific LLM provider you use today will be different in 2 years. Business logic coupled to a specific API is technical debt from day one. Abstraction keeps options open.

---

## 5. Why Mock Mode as the Learning Entry Point?

Most AI tutorials begin with: *"First, get an API key."*

This creates an invisible barrier — students without credit cards, professionals on restricted work accounts, and anyone who doesn't want to pay for experiments that might not work all hit the same wall.

Mock mode means:
- `git clone` -> `pip install` -> `python demo.py` — no credentials, no cost, no approval process
- CI/CD pipelines can test the full pipeline logic without burning tokens
- You can develop and demonstrate the agent's reasoning *structure* before any LLM is wired in

The mock decisions in `src/pipeline/mock.py` aren't random. They are:
- Grounded in real threat patterns (phishing, exfiltration, brute force, IAM abuse)
- Aligned with expert baselines (80% exact severity match by design)
- Educational artifacts in themselves — each reasoning string models good analytical thinking

---

## 6. Why ThreadPoolExecutor for Parallel Enrichment?

When processing multiple alerts simultaneously, you can either:
- **Sequential:** Alert 1 complete -> Alert 2 complete -> ...
- **Parallel:** All enrichment calls in-flight simultaneously

Enrichment (MITRE lookup, IOC context) is I/O bound, not CPU bound. Python's `ThreadPoolExecutor` handles I/O-bound parallelism with no additional dependencies.

Result: processing time scales with `max(individual alert time)`, not `sum(all alert times)`. At 10 alerts, that's roughly a 10x throughput improvement.

For a production system, you'd use async/await or a task queue (Celery, AWS SQS). ThreadPoolExecutor is the right choice for an educational project: powerful enough to be real, simple enough to understand in 10 minutes.

---

## 7. Why Two LLM Calls Per Alert (Generation + Extraction)?

The triage agent uses two separate LLM calls per alert:

1. **Generation call** (temperature=0.1): Run the ReAct loop, produce free-form analysis
2. **Extraction call** (temperature=0.0): Parse the analysis into structured JSON

Why not just ask the generation model to output JSON directly?

Because ReAct loop LLMs need *some* temperature to reason flexibly. At temperature=0.0, agents become repetitive and get stuck. But higher temperatures make structured JSON output unreliable.

Separating the concerns — high-quality reasoning at low temperature, then deterministic extraction — gets you the best of both: creative enough to reason well, reliable enough to parse.

This two-call pattern is also useful for debugging: you can inspect the raw reasoning before extraction and see exactly where the agent's thinking went wrong.
