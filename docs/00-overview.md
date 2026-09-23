# Overview

This repository is a production-oriented multi-agent research assistant built around LangGraph, typed state, and a lightweight FastAPI API.

It demonstrates the core engineering choices behind a grounded research system:

- planner, researcher, summarizer, and reporter responsibilities
- explicit state transitions instead of one monolithic prompt
- structured outputs with Pydantic
- provider abstraction for OpenAI and Anthropic
- retrieval and source metadata for better grounding
- quality checks and bounded workflow control

## Why this project exists

The goal is not to fake production readiness. It is to build a realistic portfolio project that shows how a research system can be:

- explainable
- debuggable
- stateful
- source-aware
- operationally aware of failure modes

## Repository map

- [docs/01-architecture-and-operations.md](01-architecture-and-operations.md): architecture, workflow, and operations
- [docs/02-production-and-defense.md](02-production-and-defense.md): production, security, testing, and defense questions

## Current implementation status

The project is intentionally compact but realistic:

- FastAPI app entrypoint and routes
- typed research schemas
- LangGraph workflow with a planning loop
- local fallback provider for offline validation
- smoke test to confirm the graph can execute successfully
