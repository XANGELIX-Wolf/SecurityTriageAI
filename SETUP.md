# Setup Guide

## Requirements

- **Python 3.11 or higher** — [download here](https://www.python.org/downloads/)
- **Git** — [download here](https://git-scm.com/)
- No cloud account, API key, or paid subscription required to get started

---

## Step 1 — Clone the Repo

```bash
git clone https://github.com/XANGELIX-Wolf/SecurityTriageAI.git
cd SecurityTriageAI
```

---

## Step 2 — Create a Virtual Environment

A virtual environment keeps this project's dependencies isolated from your system Python.

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You'll see `(.venv)` at the start of your prompt when the environment is active.
Run `deactivate` at any time to exit it.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs everything needed: LangChain, Jupyter, LLM providers (Ollama + Groq), and the demo UI.

> **AWS Bedrock users:** uncomment the `langchain-aws` and `boto3` lines in `requirements.txt` before installing.

---

## Step 4 — Run the Demo (Mock Mode — No API Key Needed)

```bash
python demo.py
```

You'll see the full pipeline triage 5 synthetic security alerts using pre-built mock responses — no LLM required. This is the fastest way to understand what the system does before wiring up a real model.

---

## Step 5 — Open the Curriculum Notebooks

The curriculum lives in Jupyter notebooks. With your venv active:

```bash
jupyter lab
```

This opens JupyterLab in your browser. Navigate to the `notebooks/` folder and start with `00_introduction.ipynb`.

> **Tip:** If Jupyter can't find the right Python kernel, run this once to register your venv:
> ```bash
> python -m ipykernel install --user --name=securitytriageai --display-name "SecurityTriageAI"
> ```
> Then select **SecurityTriageAI** from the kernel menu in JupyterLab.

---

## Live Mode — Connect a Real LLM (Still Free)

### Option A: Ollama (Local — Free Forever)

Runs a real LLM on your own machine. No internet required after setup.

```bash
# 1. Install Ollama
#    macOS:   brew install ollama
#    Windows/Linux: https://ollama.com/download

# 2. Pull a model (one-time ~4GB download)
ollama pull llama3.1       # best quality
# OR
ollama pull mistral        # smaller and faster

# 3. Configure
cp .env.example .env
# .env defaults to LLM_PROVIDER=ollama — no changes needed

# 4. Run
python demo.py --live
```

### Option B: Groq (Free Cloud API — No Credit Card)

Fast cloud inference using Llama 3.1. Free tier is generous for development.

```bash
# 1. Get a free API key at: https://console.groq.com

# 2. Configure
cp .env.example .env
# Edit .env and set:
#   LLM_PROVIDER=groq
#   GROQ_API_KEY=gsk_your_key_here

# 3. Run
python demo.py --live
```

---

## AWS Bedrock Mode (Interview / Production Demo)

Use this when you want to demo against a production-grade model. Costs ~$0.03–$0.30 per full run.

```bash
# 1. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret, and region (e.g. us-east-1)

# 2. Request model access in the Bedrock console
# https://console.aws.amazon.com/bedrock/home#/model-access
# Recommended: Claude 3 Haiku (cheapest) or Claude 3 Sonnet

# 3. Uncomment boto3 and langchain-aws in requirements.txt, then:
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env and set:
#   LLM_PROVIDER=bedrock
#   AWS_DEFAULT_REGION=us-east-1
#   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# 5. Run
python demo.py --live
```

---

## Provider Comparison

| Provider | Cost | Speed | Quality | Setup Effort |
|---|---|---|---|---|
| Mock | Free | Instant | Pre-built | None |
| Ollama (local) | Free | Medium | Good | Install + pull model (~10 min) |
| Groq (cloud) | Free | Very fast | Good | Free API key (~2 min) |
| Bedrock Haiku | ~$0.03/run | Fast | Excellent | AWS account + model access |
| Bedrock Sonnet | ~$0.30/run | Fast | Excellent | AWS account + model access |

---

## Troubleshooting

**`python` not found / wrong version:**
Use `python3` instead of `python`, and verify your version with `python3 --version`. Must be 3.11+.

**Jupyter kernel doesn't show your venv:**
Run `python -m ipykernel install --user --name=securitytriageai` with your venv active, then restart JupyterLab and select the **SecurityTriageAI** kernel.

**Ollama connection error:**
Make sure Ollama is running — open a separate terminal and run `ollama serve`, then retry.

**AWS credentials error:**
Run `aws sts get-caller-identity` to verify your credentials are configured correctly.
