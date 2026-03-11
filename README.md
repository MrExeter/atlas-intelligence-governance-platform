# Atlas Intelligence Governance Platform

Production-grade agentic market intelligence backend built with LangGraph,
FastAPI, and RAG with an integrated governance and evaluation layer.

---

## Live Deployment

Atlas is deployed as a gated, production-grade system.

- Dashboard: https://atlas-governance.commandercoconut.com  
- Backend API (token-gated): https://api-atlas-governance.commandercoconut.com  

Access is invitation-only via per-user Bearer tokens backed by DynamoDB with expiration and rate limiting.

Atlas takes a topic (e.g. “AI developer tools”) and produces a structured market report including:

- Executive summary  
- Market overview  
- Competitive landscape  
- Opportunities  
- Risks  
- Automated evaluation scores  

Each run produces an ExecutionTrace that enables deterministic evaluation
of reasoning steps, retrieval sources, and output claims.

This project demonstrates a full agentic pipeline — not a chatbot.

This repository is intended as a professional showcase for hiring managers and technical reviewers.

---

## Architectural Principles
- Explicit state machine (LangGraph)
- Parallel research with reducer-based merging
- Strict planner JSON contracts
- Deterministic evaluation policy
- Clear separation of scoring vs decision logic

---

## Production Architecture

Internet  
- Cloudflare DNS  
- AWS Application Load Balancer (HTTPS)  
- Private ECS Fargate task  
- DynamoDB (invite token validation)  
- AWS Secrets Manager (runtime secret injection)

Key properties:
- TLS enforced
- Private container workloads (no public IP)
- Least-privilege IAM roles
- Runtime-injected secrets (no credentials in repo)
- CloudWatch monitoring with alerting

```
Planner → Retrieval → Synthesizer → Evaluator
          ↓
     Execution Trace
          ↓
Claim Extraction → Claim Verification
          ↓
Evaluation Engine → Policy Engine
```

---

## Features

### Research Capabilities
- LangGraph-based multi-agent orchestration
- Parallel research with concurrency-safe state merging
- Modular RAG boundary
- Automated evaluation with PASS / WARN / FAIL verdicts
- Structured, executive-ready outputs
- FastAPI backend with authentication and rate limiting
- Structured logging and observability-lite metrics
- Secret-safe configuration via environment variables
- Comprehensive, risk-weighted test coverage


### Governance & Evaluation
- Claim extraction and verification
- Evidence coverage scoring
- Hallucination detection metrics
- Governance scoring and policy verdicts
- Execution trace inspection
- Token and cost tracking

---

## Security Model

- Invite-only access using hashed Bearer tokens
- Per-token rate limiting
- Expiring and revocable access tokens
- Secrets stored in AWS Secrets Manager
- No credentials committed to repository
- Production OpenAPI schema disabled
- CORS restricted to dashboard domain

---

## Non-Goals (Intentional)

Atlas deliberately does **not** include:
- A chatbot interface
- Real web scraping APIs
- Vector database persistence
- Background workers or queues

These omissions are intentional to keep the focus on backend architecture and system correctness.

---

## Current Status

- End-to-end pipeline operational
- Core architecture stabilized
- Security, rate limiting, evaluation, and observability implemented
- Suitable as a portfolio-grade reference implementation
- Future work will focus on reuse of this architecture in subsequent projects rather than expanding scope here.

---

## Tech Stack

- Python 3.11+
- FastAPI
- LangGraph
- LangChain
- OpenAI
- Pytest
- Docker (optional)
