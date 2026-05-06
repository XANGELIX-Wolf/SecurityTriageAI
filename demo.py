#!/usr/bin/env python3
"""SecurityTriageAI — Interactive Demo Script.

Runs a full alert triage pipeline demonstration with beautiful terminal output.
Works completely FREE with Ollama (local) or Groq (free cloud API).

Usage:
    python demo.py              # mock mode - zero cost, zero setup
    python demo.py --live       # real LLM (set LLM_PROVIDER in .env first)

Setup for free live mode:
    1. Install Ollama: https://ollama.com
    2. Pull a model: ollama pull llama3.1
    3. Set LLM_PROVIDER=ollama in .env
    4. Run: python demo.py --live
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.text import Text
    from rich import box
except ImportError:
    print("Run: pip install rich")
    sys.exit(1)

console = Console()

HEADER = """
 ███████╗███████╗ ██████╗    ████████╗██████╗ ██╗ █████╗  ██████╗ ███████╗
 ██╔════╝██╔════╝██╔════╝    ╚══██╔══╝██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝
 ███████╗█████╗  ██║             ██║   ██████╔╝██║███████║██║  ███╗█████╗  
 ╚════██║██╔══╝  ██║             ██║   ██╔══██╗██║██╔══██║██║   ██║██╔══╝  
 ███████║███████╗╚██████╗        ██║   ██║  ██║██║██║  ██║╚██████╔╝███████╗
 ╚══════╝╚══════╝ ╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                    AI-Powered Security Alert Triage
"""

SEVERITY_COLORS = {
    "CRITICAL": "bold red",
    "HIGH": "bold orange1",
    "MEDIUM": "bold yellow",
    "LOW": "bold green",
    "INFORMATIONAL": "dim",
    "UNKNOWN": "dim",
}


def parse_args():
    parser = argparse.ArgumentParser(description="SecurityTriageAI Demo")
    parser.add_argument("--live", action="store_true", help="Use real LLM (set LLM_PROVIDER in .env)")
    return parser.parse_args()


def load_alerts() -> list[dict]:
    path = Path("data/sample_alerts.json")
    with open(path) as f:
        return json.load(f)


def load_baselines() -> dict:
    path = Path("data/baselines/expert_triage.json")
    with open(path) as f:
        return {b["alert_id"]: b for b in json.load(f)}


def run_triage(alerts: list[dict], mock: bool) -> list[dict]:
    from src.pipeline.orchestrator import TriagePipeline
    pipeline = TriagePipeline(mock=mock)

    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} alerts"),
        console=console,
    ) as progress:
        task = progress.add_task("Triaging alerts...", total=len(alerts))
        for alert in alerts:
            progress.update(task, description=f"Analyzing: [cyan]{alert['title'][:50]}[/]")
            result = pipeline._run_mock([alert])[0] if mock else pipeline._process_one(alert)
            results.append(result)
            progress.advance(task)

    return results


def display_results(results: list[dict], baselines: dict) -> None:
    # Results table
    table = Table(
        title="\n🔍 Triage Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("Alert ID", style="dim", width=18)
    table.add_column("Title", no_wrap=False)
    table.add_column("AI Severity", justify="center", width=12)
    table.add_column("Expert", justify="center", width=10)
    table.add_column("Match", justify="center", width=6)
    table.add_column("Confidence", justify="center", width=10)
    table.add_column("Escalate", justify="center", width=8)

    matches = 0
    for r in results:
        alert_id = r.get("alert_id", "?")
        title = r.get("original_alert", {}).get("title", "")[:55] + "..."
        severity = r.get("severity", "UNKNOWN")
        baseline = baselines.get(alert_id, {})
        expert = baseline.get("expert_severity", "N/A")
        match = severity == expert
        if match:
            matches += 1
        confidence = r.get("confidence", 0)
        escalate = r.get("escalation_required", False)

        table.add_row(
            alert_id,
            title,
            Text(severity, style=SEVERITY_COLORS.get(severity, "")),
            Text(expert, style=SEVERITY_COLORS.get(expert, "dim")),
            "✅" if match else "⚠️",
            f"{confidence:.0%}",
            "🚨 YES" if escalate else "No",
        )

    console.print(table)

    # Best reasoning sample
    critical = [r for r in results if r.get("severity") == "CRITICAL"]
    if critical:
        best = critical[0]
        console.print(Panel(
            f"[bold]{best.get('original_alert', {}).get('title', '')}[/bold]\n\n"
            f"[italic]{best.get('reasoning', '')}[/italic]\n\n"
            f"[bold cyan]Recommended Actions:[/bold cyan]\n"
            + "\n".join(f"  • {a}" for a in best.get("recommended_actions", [])),
            title="[bold red]🔬 Sample Reasoning — CRITICAL Alert[/bold red]",
            border_style="red",
            padding=(1, 2),
        ))

    # Summary panel
    severity_counts = {}
    for r in results:
        s = r.get("severity", "UNKNOWN")
        severity_counts[s] = severity_counts.get(s, 0) + 1

    techniques = set()
    for r in results:
        techniques.update(r.get("mitre_techniques", []))

    avg_conf = sum(r.get("confidence", 0) for r in results) / len(results)
    escalations = sum(1 for r in results if r.get("escalation_required"))
    accuracy = matches / len(results)

    sev_str = "  ".join(
        f"[{SEVERITY_COLORS.get(k, '')}]{k}: {v}[/]"
        for k, v in sorted(severity_counts.items(), key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"].index(x[0]) if x[0] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"] else 99)
    )

    summary = (
        f"[bold]Alerts Processed:[/bold]  {len(results)}\n"
        f"[bold]Severity Distribution:[/bold]  {sev_str}\n"
        f"[bold]Escalations Required:[/bold]  [bold red]{escalations}[/bold red] of {len(results)}\n"
        f"[bold]Avg Confidence:[/bold]  {avg_conf:.0%}\n"
        f"[bold]MITRE Techniques:[/bold]  {', '.join(sorted(techniques)) or 'N/A'}\n"
        f"[bold]Accuracy vs Expert:[/bold]  [bold green]{accuracy:.0%}[/bold green] ({matches}/{len(results)} exact matches)\n"
    )

    console.print(Panel(
        summary,
        title="[bold cyan]📊 Triage Summary[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))

    console.print(Panel(
        "[bold]Stack:[/bold] AWS Bedrock · LangChain ReAct · MITRE ATT\&CK · LLM-as-Judge\n"
        "[bold]Repo:[/bold]  github.com/XANGELIX-Wolf/SecurityTriageAI\n\n"
        "[dim]Built by Devin Garrett — Security Engineer + AI Developer[/dim]\n"
        "[dim]4+ years Arctic Wolf SOC operations · CISSP · AWS AI Practitioner[/dim]",
        title="[bold]🚀 SecurityTriageAI[/bold]",
        border_style="green",
        padding=(1, 2),
    ))


def main():
    args = parse_args()
    mock = not args.live

    console.print(HEADER, style="bold cyan")

    mode_text = "[yellow]MOCK MODE[/yellow] — zero cost, no API keys needed" if mock else "[green]LIVE MODE[/green] — real LLM inference"
    console.print(Panel(mode_text, border_style="yellow" if mock else "green"))

    if mock:
        console.print("\n[dim]Tip: Run [bold]python demo.py --live[/bold] with Ollama or Groq for real LLM inference.[/dim]\n")

    alerts = load_alerts()
    baselines = load_baselines()

    console.print(f"[cyan]Loaded {len(alerts)} security alerts for triage...\n")
    time.sleep(0.5)

    results = run_triage(alerts, mock=mock)
    display_results(results, baselines)


if __name__ == "__main__":
    main()
