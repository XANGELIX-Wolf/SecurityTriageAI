# Architecture Decision Records

## ADR-001: Agent Framework — LangChain + AWS Bedrock
LangChain is explicitly listed in job requirements, integrates cleanly with Bedrock, and provides flexible tool definitions. Chosen over raw Bedrock API or managed Bedrock Agents for maximum demonstrability.

## ADR-002: Evaluation — LLM-as-Judge
Directly maps to the job requirement for "quality measurement and evaluation (e.g., LLM-as-judge)". More nuanced than accuracy metrics alone — evaluates reasoning quality at scale.

## ADR-003: Multi-Agent Architecture
Single ReAct agent (MVP) with clear path to multi-agent (V2). Simpler to debug for MVP; tools provide specialization without coordination overhead.

## ADR-004: Synthetic Data
Hand-crafted alerts with expert baselines. No real customer data. Domain expertise ensures realism. Expert baselines enable quantitative evaluation.
