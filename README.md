# Multi-Agent Research Assistant

A production-oriented portfolio project that demonstrates a LangGraph-based multi-agent research workflow for answering research questions with grounded evidence, source attribution, structured outputs, and a clean FastAPI interface.

## Project overview

This project implements a research assistant that:

- accepts a user research question
- plans the research work
- gathers evidence from tools and vector retrieval
- summarizes evidence while preserving source metadata
- generates a final research report with citations and limitations
- exposes the workflow through an API

The goal is not to pretend the system is production-ready, but to demonstrate practical engineering decisions for an AI-assisted research workflow.

## Problem

Research work requires more than a single prompt. Real systems need:

- structured planning
- explicit evidence collection
- source tracking
- tool boundaries
- controlled retry and failure handling
- observability
- safe LLM provider abstraction

This project is a compact but realistic implementation of those concerns.

## Architecture

The workflow is built around a LangGraph state graph:

`User -> Planner -> Researcher -> Quality Check -> Summarizer -> Reporter -> Final Report`

Important design choices:

- planner owns inquiry decomposition
- researcher owns evidence gathering and tool use
- summarizer owns synthesis of evidence and contradictions
- reporter owns final narrative creation using structured findings
- LangGraph owns orchestration, state, and flow control
- Qdrant provides retrieval of embedded document chunks with metadata
- FastAPI exposes a simple API surface

## Agent responsibilities

### Planner
The planner converts a research question into a structured plan with sub-questions and research tasks.

### Researcher
The researcher performs the specific tasks, retrieves relevant material, and returns evidence with source metadata.

### Summarizer
The summarizer synthesizes evidence into findings, preserving contradictions and uncertainty.

### Reporter
The reporter creates the final readable report from structured findings, with citations and limitations.

## Workflow

1. Receive a research question through the API.
2. Planner creates a structured plan.
3. Researcher executes the plan using search/retrieval tools.
4. Quality gate checks whether enough evidence exists.
5. Summarizer consolidates evidence into findings.
6. Reporter generates the final structured report.
7. Response is returned to the client with research metadata and sources.

## Technologies

- Python
- FastAPI
- Pydantic
- LangGraph
- LangChain
- OpenAI
- Anthropic / Claude
- Qdrant
- pytest

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Environment variables

The project reads these values from environment variables:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
```

## Document ingestion

The initial implementation supports simple markdown text ingestion, with an architecture designed for future pdf or txt support.

## Running the system

```bash
docker compose up
```

or locally:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## API examples

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H 'Content-Type: application/json' \
  -d '{"question":"Compare the impact of AI coding assistants on software engineering productivity."}'
```

## Example research question

> Compare the impact of AI coding assistants on software engineering productivity.

## Example output

The final report includes:

- research question
- executive summary
- key findings
- evidence
- sources
- limitations
- conclusion

## Testing

```bash
pytest
```

## Evaluation

The project includes a lightweight evaluation dataset and simple checks for planning, retrieval grounding, and report structure.

## Security

The system treats external content as untrusted and keeps agent tools narrowly scoped.

## Cost considerations

The workflow uses bounded research loops, lightweight models where possible, and metadata-based retrieval to reduce unnecessary calls.

## Limitations

- this is a learning-oriented implementation
- web search is intentionally limited or mocked in the initial version
- Qdrant and LLM provider configuration are required for full retrieval workflow

## Production architecture

Production would evolve toward:

- async job workers
- queue-based orchestration
- durable result storage
- rate limiting and tenant isolation
- richer observability and tracing

## Future improvements

- PDF ingestion
- web search tool
- async job API
- stronger evaluation harness
- user-specific research histories

## Architecture decisions

The project documentation has been condensed into a small, maintainable set:

- [docs/00-overview.md](docs/00-overview.md): project summary and goals
- [docs/01-architecture-and-implementation.md](docs/01-architecture-and-implementation.md): architecture, workflow, and operations
- [docs/02-production-and-defense.md](docs/02-production-and-defense.md): production considerations, security, and trade-offs

The interview question bank is similarly reduced to:

- [questions/00-master-interview-questions.md](questions/00-master-interview-questions.md)
- [questions/01-architecture-and-multi-agent.md](questions/01-architecture-and-multi-agent.md)
- [questions/02-production-security-and-defense.md](questions/02-production-security-and-defense.md)


## RAG milestone

The research workflow can now use Qdrant as a second evidence source in addition to web search.

### Local knowledge indexing

Place Markdown documents under `knowledge/`, configure `OPENAI_API_KEY`, then call `POST /api/v1/knowledge/index`. The ingestion pipeline cleans Markdown, creates overlapping chunks, generates OpenAI embeddings, stores vectors in Qdrant, and makes retrieved chunks available to the Researcher as structured evidence.

Each indexed chunk keeps document ID, title, source, chunk index, and content metadata for traceability.

This milestone intentionally keeps indexing synchronous and Markdown-only. PDF parsing, durable document metadata, tenant isolation, background ingestion, and hybrid retrieval remain later extensions so the current Vercel deployment is not disrupted.


## Research quality evaluation

The workflow now computes evidence-quality metadata before returning a report. The score considers evidence coverage, source diversity, citation coverage, and groundedness. The final report confidence is capped by this quality score, and limitations are augmented when evidence quality is weak. The API exposes the quality metadata so the frontend or future evaluation dashboard can inspect why confidence is limited.


## Claim-level grounding

The report pipeline now performs a deterministic post-generation grounding check. Each structured finding is compared with its linked and retrieved evidence, producing a support score, citation IDs, contradiction count, and warnings for weakly supported claims. Weak claim grounding reduces the final quality/confidence metadata instead of allowing a high-confidence report to hide unsupported findings.
