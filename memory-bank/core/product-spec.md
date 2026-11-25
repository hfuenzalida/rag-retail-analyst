# Product Spec — RAG Retail Analyst

## Overview

Sovereign AI RAG Data Analyst for small retail businesses: inventory and sales analytics with evidence-linked answers and actionable recommendations.

## User Personas

- **Managers / store owners** — plain-language questions, summaries, recommended actions.
- **Operations analysts** — filters, deep dives, threshold configuration.

## Key Outcomes (v1)

- Explain revenue and inventory changes with drivers.
- Identify stock-out risk and reorder suggestions.
- Ground every claim in metrics or documents; abstain when data is missing.

## Non-Functional Requirements

- Data stays on client infrastructure (sovereign/local-first).
- Hybrid local/cloud LLM with strict sensitivity routing.
- Typical query latency: <5s; heavy queries <15s.
- Audit logging for queries, routing, and model calls.

## v1 Scope

- Single business per deployment (multi-tenant extensibility via `client_id`).
- Data sources: PostgreSQL/MySQL, CSV uploads.
- Core tables: `sales`, `inventory`, `products`.
