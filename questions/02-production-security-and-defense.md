# Production, Security, and Defense

## What would you do before calling this production-ready?

The biggest next steps are durable storage, async orchestration, stronger observability, tenant isolation, and better evaluation harnesses. The project already provides the architectural foundation, but not the full operational maturity of a production service.

## Why is tool scoping important?

The project intentionally limits tool behavior to narrow, well-defined actions. That reduces the chance of a research agent doing harmful or unexpected operations.

## How does the project handle untrusted content?

It assumes retrieved content may be noisy, deceptive, or manipulated. That is why source metadata, grounded output, and conservative synthesis matter.

## How would you defend this architecture in an interview?

The strongest defense is to explain the reasoning behind each subsystem: graph orchestration, state typing, provider abstraction, retrieval grounding, and explicit quality checks. These are all practical engineering choices, not just AI buzzwords.

## What is the biggest limitation of the current repo?

The biggest limitation is that it remains a compact learning implementation. It demonstrates the pattern well, but it still needs stronger production controls, evaluation, and operational guardrails before real-world deployment.
