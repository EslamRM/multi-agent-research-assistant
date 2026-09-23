# Architecture and Implementation Guide

## 1. System purpose

This project is a learning-focused but production-oriented research assistant. It accepts a research question, decomposes the work, gathers evidence, summarizes the material with source grounding, and returns a report with citations and limitations.

The system is intentionally designed to show the practical engineering decisions behind an AI workflow rather than a single prompt wrapper.

## 2. Core architecture

The project is organized around a LangGraph workflow with explicit state.

Flow:

- User request enters the system
- Planner turns the question into tasks and sub-questions
- Researcher gathers evidence from tools and retrieval
- Quality check validates evidence sufficiency
- Summarizer synthesizes the evidence into findings
- Reporter turns the synthesis into a final narrative

This keeps responsibilities separated so each agent owns one layer of the workflow.

## 3. Project structure

- backend/app/main.py: FastAPI application entrypoint
- backend/app/api/routes/research.py: API routes for research requests
- backend/app/graph/state.py: state model and coercion logic
- backend/app/graph/workflow.py: LangGraph orchestration
- backend/app/llm/interface.py: provider abstraction
- backend/app/llm/factory.py: provider selection logic
- backend/app/tools/search.py: narrow tool interface for sources
- backend/app/rag/retriever.py: retrieval layer
- backend/app/rag/ingestion.py: source ingestion logic
- backend/app/schemas/research.py: Pydantic models for requests, plans, evidence, reports
- backend/app/services/research.py: orchestrating service layer

## 4. Typed state and schemas

The project uses Pydantic models rather than loose dictionaries for key outputs. This provides:

- validation at model boundaries
- consistent serialization and state transfer
- easier debugging when the model emits unexpected output
- safer composition between workflow nodes

The `ResearchState` dataclass holds the workflow memory. LangGraph often emits dict-like structures at runtime, so a coercion helper converts graph output back into the typed state before continuing.

## 5. Multi-agent responsibilities

### Planner
The planner turns a question into a structured list of sub-questions and tasks. It owns decomposition and goal setting.

### Researcher
The researcher gathers sources and evidence. It uses tool and retrieval outputs, then records source metadata for later grounding.

### Summarizer
The summarizer combines evidence into claims, contradictions, and limitations without producing final polished prose.

### Reporter
The reporter writes the final answer, citing the underlying evidence and being transparent about uncertainty.

## 6. Tool calling and retrieval

The project intentionally keeps tooling narrow. The search tool is scoped to a limited set of retrieval behaviors instead of open-ended execution.

This matters because real-world AI agents can become dangerous when they are allowed to perform arbitrary actions. Narrow tools reduce execution risk and make debugging straightforward.

The retrieval layer is intentionally simple but realistic: chunked documents are stored with metadata, retrieved by semantic similarity, and then passed into the research flow.

## 7. LLM providers and fallback behavior

The code abstracts the provider behind a single interface so the workflow can work with OpenAI, Anthropic, or a local fallback.

This is useful because:

- provider issues should not leak into core workflow logic
- tests can run even without external API keys
- the project remains portable for demos and local learning

The local fallback is not a production replacement for a real model, but it keeps the system runnable and explainable.

## 8. Error handling and quality checks

The workflow includes a quality check before summarization. This is intended to ensure that enough evidence exists before the system proceeds.

By default, the project keeps failure handling explicit and conservative:

- if evidence is weak, the flow can stop or degrade gracefully
- if provider configuration is missing, the local fallback can be used
- state carries metadata for debugging and observability

## 9. Security posture

This project treats external content as untrusted. In a research workflow, retrieved documents and web content may include injection-like instructions or manipulated text.

The project reduces risk by:

- limiting tools to narrow, well-defined actions
- separating agent responsibilities
- grounding answers in source metadata
- avoiding unrestricted execution capabilities

This is the right starting point for a safer architecture, though a production system would need stricter sandboxing, policy enforcement, and auditing.

## 10. Why this architecture is useful

This design demonstrates the core patterns behind many practical AI systems:

- orchestration with stateful graphs
- typed interfaces across agent boundaries
- retrieval-grounded reasoning
- explicit evidence tracking
- clear separation between synthesis and final presentation

The value is not just academic; it makes the system easier to debug, explain, and defend in interviews.
