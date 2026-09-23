# Production, Security, and Defense Guide

## 1. Production readiness

This project is intentionally described as production-oriented but not production-ready. That distinction matters.

A realistic production path would add:

- async background jobs for long-running research
- durable storage for request and result state
- queue-based orchestration for scale and retry
- tenant isolation and access control
- rate limiting and fair usage controls
- stronger observability and tracing

The current implementation demonstrates the right architectural building blocks without pretending the system is fully hardened.

## 2. Reliability and quality

The workflow keeps limits explicit:

- bounded research loops
- lightweight provider fallback
- evidence sufficiency checks before final synthesis
- typed state to reduce schema drift

The key principle is to make failure modes visible rather than silent. If evidence is weak, the system should not pretend certainty.

## 3. Observability

A real system should log:

- request ID and question hash
- node execution timing
- evidence count and source count
- summary and report generation steps
- structured errors with retry metadata

This helps support debugging and performance tuning when the workflow is running under real load.

## 4. Cost optimization

The project is designed to avoid waste.

Good controls include:

- limiting source counts and retrieval depth
- bounding research iterations
- preferring retrieval over giant context windows when possible
- using smaller or fallback models for less critical stages
- tracking quality signals to justify model choice

AI systems can become expensive quickly if every node is allowed to over-consume context and tokens.

## 5. Security and prompt injection

This project treats retrieved content as untrusted by default. That is a key design requirement for research assistants that ingest external material.

Security concerns include:

- prompt injection through source text
- malicious or manipulated search results
- tool misuse when an agent is over-permissioned
- leakage of private data through uncontrolled prompts

The architecture reduces risk by keeping tool scope narrow, separating responsibilities, and grounding final outputs in source metadata rather than unverified model output.

## 6. Architecture decisions worth defending

The most important design choices in this repo are:

- use a graph instead of a giant function
- keep tools narrow and explicit
- use typed schemas and state transitions
- separate planning from execution from final synthesis
- preserve source metadata for trust and traceability

These choices make the system easier to explain and defend in an interview.

## 7. What would we change before production?

Before taking this beyond a portfolio project, we would likely add:

- async API endpoints
- persistent vector storage and richer retrieval pipelines
- user session management and authorization
- structured evaluation harnesses
- proper monitoring, alerting, and incident response

The current project is a strong foundation for that next stage, but it is still intentionally a thoughtful learning architecture rather than the final product.
