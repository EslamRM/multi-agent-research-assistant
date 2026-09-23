# Architecture and Multi-Agent Design

## Why is this a multi-agent system instead of a single prompt?

The workflow separates planning, evidence gathering, synthesis, and final writing into different responsibilities. This keeps the behavior more interpretable and easier to debug than one giant prompt that tries to do everything at once.

## Why does the planner exist separately from the researcher?

The planner decides what questions to answer and what tasks to pursue. The researcher is responsible for evidence collection and retrieval. Splitting these roles makes the system more modular and makes quality issues easier to localize.

## Why is state explicit?

The project uses a typed `ResearchState` rather than passing loose dictionaries through the workflow. This reduces errors, clarifies node contracts, and makes the execution graph easier to defend.

## Why does the summarizer stay separate from the reporter?

Synthesis and presentation are different jobs. A summarizer can aggregate findings and contradictions. A reporter can turn that into a coherent final narrative with limitations and conclusions.

## What is the trade-off between agent separation and complexity?

More agents create more structure, but they also create more interfaces and more opportunities for mismatch. The project keeps the system intentionally small, which is a good balance for a portfolio and learning project.
