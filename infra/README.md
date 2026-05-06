# Infrastructure

AWS CDK stacks for SecurityTriageAI deployment.

## Stacks

- **TriageStack** — Core infrastructure (DynamoDB, SQS, Step Functions)
- **BedrockStack** — Bedrock model access and guardrails  
- **ObservabilityStack** — CloudWatch dashboards, alarms, X-Ray tracing

## Deployment

```bash
cd infra
npm install
cdk bootstrap
cdk deploy --all
```

## Architecture Decisions

- **Step Functions** over Lambda-only: Better visibility into multi-step agent workflows
- **DynamoDB** for results: Cost-effective, auto-scales, TTL for cleanup
- **SQS** for ingestion: Decouples alert sources from processing, provides retry/DLQ
- **Bedrock** over self-hosted: Managed scaling, no GPU infrastructure to maintain
