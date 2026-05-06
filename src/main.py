"""SecurityTriageAI - Main entry point."""

import argparse
import json
import sys
from pathlib import Path

import structlog

from src.pipeline.orchestrator import TriagePipeline

logger = structlog.get_logger()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SecurityTriageAI - Autonomous alert triage agent")
    parser.add_argument("--input", type=Path, default=Path("data/sample_alerts.json"))
    parser.add_argument("--output", type=Path, default=Path("output/triage_results.json"))
    parser.add_argument("--evaluate", action="store_true", help="Run LLM-as-judge evaluation after triage")
    parser.add_argument("--model-id", type=str, default="anthropic.claude-3-sonnet-20240229-v1:0")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info("starting_triage_pipeline", input=str(args.input), model=args.model_id)

    if not args.input.exists():
        logger.error("input_not_found", path=str(args.input))
        return 1

    with open(args.input) as f:
        alerts = json.load(f)

    logger.info("alerts_loaded", count=len(alerts))
    pipeline = TriagePipeline(model_id=args.model_id)
    results = pipeline.run(alerts)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info("triage_complete", results_count=len(results), output=str(args.output))

    if args.evaluate:
        from src.evaluation.judge import evaluate_results
        scores = evaluate_results(results)
        logger.info("evaluation_complete", avg_score=scores["average"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
