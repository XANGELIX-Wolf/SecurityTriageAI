# Setup Guide

## Quick Start — Free (Mock Mode, Zero Setup)

```bash
git clone https://github.com/XANGELIX-Wolf/SecurityTriageAI.git
cd SecurityTriageAI
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python demo.py
```

That's it. No API keys, no AWS account, no cost.

---

## Free Live Mode — Ollama (Local LLM)

Runs a real LLM on your Mac. Completely free.

```bash
# 1. Install Ollama
brew install ollama        # or: https://ollama.com

# 2. Pull a model (one-time, ~4GB download)
ollama pull llama3.1       # best quality
# OR: ollama pull mistral  # smaller/faster

# 3. Configure
cp .env.example .env
# .env is already set to LLM_PROVIDER=ollama — no changes needed

# 4. Run
python demo.py --live
```

---

## Free Live Mode — Groq (Free Cloud API)

Fast cloud inference. Free API key, no credit card.

```bash
# 1. Get free API key: https://console.groq.com

# 2. Configure
cp .env.example .env
# Edit .env:
#   LLM_PROVIDER=groq
#   GROQ_API_KEY=gsk_your_key_here

# 3. Run
python demo.py --live
```

---

## AWS Bedrock Mode (Interview Demo)

Switch to Bedrock for a live interview demo. Cost: ~$0.05–0.50 per full run.

```bash
# 1. Configure AWS credentials
aws configure

# 2. Enable model access in Bedrock console
# https://console.aws.amazon.com/bedrock/home#/model-access
# Request: Claude 3 Haiku (cheapest) or Claude 3 Sonnet

# 3. Configure
cp .env.example .env
# Edit .env:
#   LLM_PROVIDER=bedrock
#   AWS_DEFAULT_REGION=us-east-1
#   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# 4. Run
python demo.py --live
```

**Estimated cost per full demo run (5 alerts):**
- Claude 3 Haiku: ~$0.03
- Claude 3 Sonnet: ~$0.30

---

## Provider Comparison

| Provider | Cost | Speed | Quality | Setup |
|---|---|---|---|---|
| Mock | Free | Instant | N/A | None |
| Ollama | Free | Slow-Medium | Good | Install + pull model |
| Groq | Free | Very fast | Good | Free API key |
| Bedrock (Haiku) | ~$0.03/run | Fast | Excellent | AWS account |
| Bedrock (Sonnet) | ~$0.30/run | Fast | Excellent | AWS account |
