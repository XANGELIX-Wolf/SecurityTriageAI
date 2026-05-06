# SecurityTriageAI — Learning Curriculum

A structured path for security practitioners building their first agentic AI system.

---

## Prerequisites

**Required:**
- Python basics (functions, classes, imports, pip)
- Comfort with the terminal / command line
- Basic understanding of what a security alert is

**Helpful but not required:**
- Familiarity with JSON
- Any experience with APIs or HTTP
- SOC analyst or security engineering background (gives context, not required for the code)

**Not required:**
- Prior AI or ML experience
- AWS account or cloud credits
- Any paid subscriptions of any kind

---

## Module 00: Why Agentic AI for Security?

📓 **Notebook:** [00_introduction.ipynb](notebooks/00_introduction.ipynb)
⏱️ **Estimated time:** 30 minutes

### Learning Objectives
By the end of this module, you will be able to:
- Explain the three main failure modes of rule-based alert triage
- Distinguish between a simple LLM prompt and an agentic system
- Run the SecurityTriageAI demo in mock mode and interpret all output panels
- Articulate the AI-as-augmentation mental model for security operations

### Key Concepts
- **Alert fatigue**: Why volume + noise is the core SOC operational problem
- **The rules trap**: Why SIEM rules can't generalize to novel attack patterns
- **Agentic AI**: Systems that reason, use tools, and course-correct
- **AI as a junior analyst**: The right mental model for human-AI collaboration in security

### What You'll Build
Run the full demo and understand what each panel represents. No code changes required.

### Discussion Questions
1. Where do rule-based systems fail most often in the security contexts you've seen?
2. What would it take for you to trust an AI's triage decision enough to act on it without review?
3. What information would you always want the AI to explain when it escalates something as Critical?

---

## Module 01: ReAct Agents — Think, Act, Observe

📓 **Notebook:** [01_react_agent.ipynb](notebooks/01_react_agent.ipynb)
⏱️ **Estimated time:** 60–90 minutes

### Learning Objectives
By the end of this module, you will be able to:
- Explain the ReAct (Reason + Act) loop and why it outperforms simple prompting for structured reasoning tasks
- Read and trace the triage agent implementation in `src/agents/triage_agent.py`
- Understand how structured output extraction works (reliable JSON from free-form LLM text)
- Describe each tool available to the agent and what it does

### Key Concepts
- **ReAct loop**: Think → Act → Observe → Think again (until done or max steps)
- **Tools**: Functions the agent calls mid-reasoning (MITRE lookup, IP enrichment, severity scoring)
- **Structured output**: Reliably extracting JSON from free-form LLM responses
- **Prompt engineering**: How the system prompt shapes agent behavior and output quality

### Code Focus: `src/agents/triage_agent.py`

The ReAct loop, simplified:
```python
while not done and step < max_steps:
    thought = llm.invoke(prompt + history)    # Agent reasons
    action  = parse_action(thought)           # What does it want to do?
    result  = tools[action.name](action.input)# Execute the tool
    history += f"\nObservation: {result}"     # Agent sees the result
    done = "Final Answer:" in thought
```

### Exercises

**Beginner:** Run `python demo.py` and identify which MITRE techniques the agent maps each alert to.

**Intermediate:** Open `src/agents/triage_agent.py` and modify `TRIAGE_PROMPT`. Add: `"When in doubt between severity levels, prefer the lower one."` Run the demo again — did any severities change? Check evaluation scores.

**Advanced:** Add a new `IPReputationTool` to `src/tools/` that looks up source IPs against a hardcoded blocklist. Wire it into `TriageAgent.__init__` and update the prompt. Verify the agent uses it when processing ALERT-2024-002.

---

## Module 02: Running for Free — LLM Provider Strategy

📓 **Notebook:** [02_llm_providers.ipynb](notebooks/02_llm_providers.ipynb)
⏱️ **Estimated time:** 45 minutes

### Learning Objectives
By the end of this module, you will be able to:
- Switch between LLM providers using only environment variables (no code changes)
- Explain the trade-offs between mock, local (Ollama), cloud-free (Groq), and cloud-paid (Bedrock)
- Understand the factory pattern for abstracting infrastructure dependencies
- Get the full pipeline running against a real LLM for $0

### The Provider Ladder

| Provider | Cost | Speed | Quality | Best For |
|---|---|---|---|---|
| **Mock** | $0 | Instant | Pre-built | CI/CD, learning pipeline structure |
| **Ollama** (local) | $0 forever | 2–5s | Good | Development, notebooks, learning |
| **Groq** (free tier) | $0 (rate limited) | ~0.5s | Great | Development, demos, sharing |
| **Bedrock** (Claude Haiku) | ~$0.03–0.10/run | ~1–2s | Excellent | Production, formal demos |

### Key Concept: The Factory Pattern

```python
# src/llm/factory.py — the entire LLM decision in one function
def get_llm(provider=None):
    provider = provider or os.getenv("LLM_PROVIDER", "ollama")
    if provider == "ollama":    return ChatOllama(...)
    elif provider == "groq":    return ChatGroq(...)
    elif provider == "bedrock": return ChatBedrock(...)
```

One environment variable. Zero code changes. This is how production AI systems stay provider-flexible.

### Exercises

**Beginner:** Get mock mode running, then set up Groq (free key at console.groq.com). Compare the reasoning outputs for the same alert. What's different?

**Intermediate:** Add a fourth provider to `src/llm/factory.py` — OpenAI (`langchain-openai`, `ChatOpenAI`). You don't need a key to write and test the code.

**Advanced:** Build a cost-tracking wrapper that logs token usage and estimated cost per provider per run. Print a report after each demo: `Total tokens: X | Estimated cost: $Y`.

---

## Module 03: Evaluation — Teaching AI to Grade Its Own Work

📓 **Notebook:** [03_evaluation.ipynb](notebooks/03_evaluation.ipynb)
⏱️ **Estimated time:** 45–60 minutes

### Learning Objectives
By the end of this module, you will be able to:
- Explain the LLM-as-judge evaluation pattern and when it applies
- Interpret evaluation dimension scores and understand what drives each one
- Write an evaluation rubric that reflects real SOC analyst quality standards
- Design a regression test to catch silent AI quality degradation

### Key Concepts
- **Ground truth baselines**: Expert-labeled triage decisions as the reference answer
- **LLM-as-judge**: Using an LLM to evaluate another LLM's output against a rubric
- **Evaluation dimensions**: Why 5 specific scores tell you more than one overall accuracy number
- **Regression testing**: Ensuring AI quality doesn't silently degrade when you change prompts or models

### The 5 Evaluation Dimensions

| Dimension | What It Measures |
|---|---|
| **Severity Accuracy** | Is Critical / High / Medium / Low correct vs. expert baseline? |
| **ATT&CK Mapping** | Did the agent identify the right MITRE technique(s)? |
| **Reasoning Quality** | Is the chain-of-thought logical, grounded, and coherent? |
| **Actionability** | Are recommended actions specific, executable, and relevant? |
| **Completeness** | Did the agent address all key indicators in the alert? |

### Why 80% Is a Strong Starting Point

The mock demo shows 80% exact-match accuracy (4/5 alerts match expert baselines on severity). In production security AI, 80% on a well-defined rubric — with human review of the remaining 20% — is more valuable than a manual process that's 70% accurate but consumes 100% of analyst time.

The goal isn't to eliminate human judgment. It's to make human judgment faster and less fatiguing.

### Exercises

**Beginner:** Read through `data/sample_alerts.json` and write your own triage decision for each alert. Compare to the AI output. Where do you agree? Where do you disagree?

**Intermediate:** Design a 6th evaluation dimension — "False Positive Risk" — that scores how well the agent assesses whether the alert might be a false positive. Write the rubric.

**Advanced:** Build a regression test harness using pytest. Run evaluation, store baseline scores. Fail the test if any dimension drops more than 10 points from baseline. Integrate with `.github/workflows/`.

---

## Further Reading

### Agentic AI
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Original paper
- [LLM-as-Judge (MT-Bench)](https://arxiv.org/abs/2306.05685) — The evaluation pattern we implement
- [LangChain Agents Documentation](https://python.langchain.com/docs/modules/agents/)

### Security AI
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [NIST AI Risk Management Framework](https://airc.nist.gov/)
- [CISA Guidance on AI in Cybersecurity](https://www.cisa.gov/ai)

### Free LLM Providers
- [Ollama](https://ollama.ai) — Run LLMs locally, forever free
- [Groq](https://console.groq.com) — Free cloud API tier, no credit card
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) — Pay-per-token, free tier for new accounts
