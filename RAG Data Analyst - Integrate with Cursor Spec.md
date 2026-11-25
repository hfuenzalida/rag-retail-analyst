# 8. Integrate with Your Chosen Vibe Coding Platform

This section defines how the RAG Data Analyst suite should be integrated into **Cursor** using modern `.cursor/rules/*.mdc` rules, path-scoped guardrails, memory-bank bootstrapping, and a small set of repeatable workflow commands. Cursor’s rule system works best when it is **modular, narrow, and attached only where relevant**, rather than implemented as a single monolithic instruction file.[web:212][web:214][web:218]

For this suite, Cursor is not just an editor assistant; it becomes a **local architectural enforcement layer**. By encoding architecture, stack, agent boundaries, testing rules, and memory-bank workflow directly into Cursor, the development loop stays fast without drifting into unsafe prompt-driven code generation.[file:227][file:199][file:184]

---

## 1. Cursor Rule Architecture

### 1.1 Layered Rule System

The suite should adopt a **layered rule framework** in Cursor rather than a single master rule file.[file:227][web:214][web:218]

Recommended structure:

- **Always-on core rules**
  - small, persistent rules that define the project’s foundational architecture and canonical stack.
- **Auto-attached path-scoped rules**
  - rules that activate only for matching files or directories.
- **Optional manual workflow rules**
  - special rules or commands used for implementation slices, quality checks, or memory synchronization.[file:227]

This pattern minimizes token overhead, reduces instruction fatigue, and keeps Cursor focused on the specific constraints relevant to the file being edited.[web:214][web:218]

### 1.2 Avoid a Monolithic Master Rule

A single giant rule file containing architecture, testing, prompts, security, and workflow instructions should be avoided.[file:227] Large rule monoliths consume unnecessary context space and make it easier for the assistant to miss or dilute critical constraints.[web:214][web:216]

---

## 2. Recommended `.cursor/rules/` Categories

The Cursor integration should use the following isolated `.mdc` categories:[file:227][file:154]

- `architecture.mdc`
- `stack.mdc`
- `agents.mdc`
- `security.mdc`
- `testing.mdc`
- `memory-bank.mdc`
- `implementation-workflow.mdc`
- `quality-gates.mdc`

A `frontend.mdc` file can be added later, but for v1 the Cursor integration should focus primarily on **backend + memory-bank**, because those layers define the core analytical behavior and contracts of the suite.[file:227][file:154]

### 2.1 Always-On Rules

Keep the always-on global footprint intentionally small:

- **`architecture.mdc`**
  - teaches Cursor the layer boundaries and directory isolation rules.
- **`stack.mdc`**
  - locks in the canonical stack: FastAPI, Pydantic AI, PostgreSQL/pgvector, local LLM runtime, optional cloud providers.[file:227][file:154]

These should remain globally active so Cursor always understands the project’s structural and technical foundation.

### 2.2 Auto-Attached Rules

The following rules should attach only when relevant:

- **`agents.mdc`** → `backend/app/agents/**`
- **`security.mdc`** → `backend/app/core/**`, `backend/app/agents/**`, `backend/app/tools/routing_tools.py`, `backend/app/tools/eval_tools.py`
- **`testing.mdc`** → `backend/tests/**`, plus agent/tool/core files when mutated
- **`memory-bank.mdc`** → `memory-bank/**/*.md`
- **`implementation-workflow.mdc`** → manual or targeted use during feature-slice execution
- **`quality-gates.mdc`** → attached during Red Zone or testing-sensitive changes.[file:227]

This keeps detailed rules dormant unless they are actually needed.

---

## 3. Path and Glob Mapping

### 3.1 Backend Folder Mapping

Cursor should use strict path mapping for backend files:[file:227][file:154]

- `backend/app/api/**`
  - attach API-layer structure and endpoint rules.
- `backend/app/agents/**`
  - attach agent role, prompt, and multi-agent isolation rules.
- `backend/app/tools/**`
  - attach tool-surface restrictions and test expansion rules.
- `backend/app/core/**`
  - attach configuration, security, and environment rules.
- `backend/tests/**`
  - attach testing conventions, fixture, and isolation rules.

This ensures the assistant edits each layer according to its operational role instead of using generic full-stack assumptions.

### 3.2 Memory-Bank Mapping

For markdown operational memory, Cursor should attach a general rule to:

- `memory-bank/**/*.md`

But it should apply **stricter governance** to:

- `memory-bank/core/**`
- `memory-bank/agents/**`

These hold architectural contracts, workflow rules, and prompt design documents, so they should be treated as controlled files rather than casual documentation.[file:227][file:154]

### 3.3 Frontend Scope for v1

Cursor integration should initially prioritize:

- backend code,
- tests,
- memory-bank,
- prompt/config files.[file:227]

Frontend-specific Cursor rules can be added later, once backend schemas and `QueryResponse` structures are stable.[file:154]

---

## 4. Memory-Bank Bootstrapping Rules

### 4.1 Required Files Before Backend Work

Before Cursor edits backend logic, it must read and reference the core memory-bank files that define the suite’s contracts and architecture.[file:227][file:199][file:154]

Required bootstrap sequence:

1. `memory-bank/core/agent-surface.md`
2. `memory-bank/core/architecture.md`
3. `memory-bank/core/testing-strategy.md`
4. `memory-bank/core/implementation-plan.md`

These files define:
- data and tool contracts,
- module boundaries,
- validation requirements,
- and the current implementation step being executed.[file:154][file:141][file:184]

### 4.2 Refusal Behavior

Cursor should be explicitly instructed to **refuse implementation work** when these files are not referenced or loaded into context first.[file:227][file:199]

Expected refusal pattern:

> “Please reference the matching memory-bank file to verify architectural alignment before editing.”

This refusal behavior is essential to prevent ad-hoc code generation that bypasses the documented architecture and workflow system.[file:227]

---

## 5. Task Workflow Enforcement in Cursor

### 5.1 Five-Phase Implementation Pipeline

Cursor should enforce the same five-phase task flow already defined for the suite:[file:199][file:184][file:227]

1. **Plan Refinement**
2. **Code Generation**
3. **Auto-Run Tests**
4. **Auto-Run Offline Eval Subset**
5. **Human Review + Commit**

This means Cursor is not allowed to behave like a one-shot code writer. It must move through a structured implementation loop aligned with your vibe-coding workflow.[file:199]

### 5.2 Split Workflow Rules

Rather than encoding all workflow logic into one file, use two clean rule modules:[file:227]

- **`implementation-workflow.mdc`**
  - governs feature-slice execution flow, plan alignment, and context loading.
- **`quality-gates.mdc`**
  - governs tests, eval thresholds, mocking rules, and validation expectations.

This separation keeps the workflow readable and maintainable.

---

## 6. Red Zone and Green Zone in Cursor

### 6.1 Red Zone Paths

Cursor must treat the following as **Red Zone** paths where it may propose diffs but must not freely auto-apply broad or architectural mutations:[file:227][file:170][file:184][file:199]

- `backend/app/core/**`
- `backend/app/agents/**`
- `backend/app/tools/routing_tools.py`
- `backend/app/tools/eval_tools.py`
- `backend/app/tools/*` files involving financial or metric-critical logic
- `backend/app/agents/prompts/*.yaml`
- `memory-bank/core/**`
- `memory-bank/agents/**`

For these paths, Cursor may:

- draft changes,
- show isolated diffs,
- propose tests and prompt updates,

but human approval remains mandatory before adoption.[file:227]

### 6.2 Green Zone Paths

Cursor may operate with higher autonomy in **Green Zone** areas such as:

- documentation,
- non-sensitive helper utilities,
- frontend UI views and panels (later phase),
- data visualizations,
- local string formatting or superficial UX helpers.[file:227][file:199][file:170]

This preserves fast iteration where the architectural blast radius is low.

---

## 7. Agent-Aware Cursor Rules

### 7.1 Cursor Must Know the Internal Agent Roster

Cursor rules should explicitly encode the suite’s five internal agent roles:[file:227][file:154]

- RAG Analyst Agent
- Evaluator Agent
- Ingestion / Schema Mapping Agent
- Routing / Sensitivity Agent
- Ops / Maintenance Agent

These roles should be described in `agents.mdc` so Cursor understands their responsibilities and does not generate generic “assistant” code that blurs role boundaries.

### 7.2 Structural Preservation Rule

Cursor must be instructed to **preserve agent isolation**:

- do not collapse multiple agents into one monolithic class,
- do not merge prompt responsibilities casually,
- do not centralize all tools into a universal helper layer without architectural justification.[file:227]

This rule is critical because multi-agent separation is part of the suite’s safety, observability, and testing model.[file:184][file:154]

---

## 8. Prompt and Config Storage Conventions

### 8.1 Runtime Source of Truth

Cursor should treat:

- `backend/app/agents/prompts/*.yaml`

as the **runtime source of truth** for executable prompts and agent configuration.[file:227]

Meanwhile:

- `memory-bank/agents/*.md`

should serve as human-readable design documents and review artifacts rather than runtime prompt files.[file:227]

### 8.2 Hard Separation of Logic and Prompts

Cursor rules should explicitly encode the following structural boundary:[file:227][file:141]

- executable logic stays in Python,
- prompts and tool descriptions live in YAML or Markdown,
- prompt edits are Red Zone operations,
- prompt design docs in memory-bank may inform code, but they are not the runtime execution layer.

This protects the codebase from prompt sprawl and makes prompt governance testable and versionable.

---

## 9. Testing and Eval Hooks in Cursor

### 9.1 Mandatory Test Expansion

Cursor must be instructed that any mutation to:

- tools,
- agents,
- routing,
- evaluation logic,
- or schema-sensitive core behavior

requires corresponding updates to:

- unit tests,
- integration tests,
- and relevant golden-question coverage.[file:227][file:184]

This aligns Cursor with the suite’s quality-gate model instead of allowing silent regressions.

### 9.2 Automatic Fast Verification

After applying feature changes in critical paths, Cursor should automatically trigger a **fast local validation pass** before handing control back to you.[file:227]

Typical validation includes:

- focused `pytest` subset,
- schema validation,
- and, where relevant, a minimal offline eval slice from the golden dataset.[file:184]

This is not meant to replace full CI or nightly evals, but to catch local regressions immediately.

---

## 10. Git and Workflow Placement

Cursor should follow the broader project Git strategy:

- one feature slice per branch,
- conventional commits,
- draft PR preparation with tests and eval summaries.[file:199][file:227]

However, the detailed Git and PR instructions should **not** consume too much `.mdc` rule space. Those broader workflow instructions are better stored in a top-level project guide such as `CLAUDE.md`, while Cursor’s `.mdc` rules remain focused on file-level editing behavior and architectural guardrails.[file:227]

---

## 11. Cursor Custom Commands

To support high-frequency workflows, the Cursor integration should define a small set of reusable commands.[file:227][web:224]

Recommended high-leverage commands:

- **`/plan-feature`**
  - read memory-bank files and draft an isolated implementation step aligned with `implementation-plan.md`.
- **`/implement-slice`**
  - execute a scoped feature slice against the current implementation milestone.
- **`/check-gates`**
  - run unit tests plus a fast local eval subset relevant to the modified paths.
- **`/sync-progress`**
  - scan recent workspace changes and update `progress.md` / implementation tracking docs.

These commands reinforce the suite’s preferred cadence: spec → slice → verify → document.

---

## 12. Rule Writing Style and Portability

### 12.1 Rule Verbosity

The `.mdc` rules should be kept **short, strict, and constraint-driven** rather than highly narrative.[file:227][web:214]

Short rules are preferable because they:

- reduce token overhead,
- improve compliance,
- reduce ambiguity,
- and are easier to maintain as the suite evolves.[web:214][web:218]

### 12.2 Portability Layer

The modern rule system should use:

- `.cursor/rules/*.mdc`

as the primary Cursor configuration layer.[file:227]

For portability across tools and future reuse, the project should also keep a lightweight root guidance file such as:

- `CLAUDE.md`
- or an equivalent compatibility doc / root rule artifact.[file:227]

This provides cross-tool continuity without overloading Cursor’s path-scoped rule files.

---

## 13. Recommended Cursor Integration Outcome

The final Cursor integration for this suite should produce a development environment where:

- Cursor always understands the canonical architecture and stack,
- backend edits are blocked unless memory-bank context is loaded,
- Red Zone files are protected by propose-only behavior,
- prompt and agent boundaries remain explicit,
- tests and evals are tied directly to code changes,
- and repeated vibe-coding workflows are compressed into a handful of reliable commands.[file:227][file:199][file:184]

In practical terms, this means Cursor becomes a **live enforcement mechanism** for the same design principles already defined in the suite:

- strict feature-slice execution,
- grounded agent boundaries,
- secure local/cloud routing,
- strong quality gates,
- and controlled prompt evolution.[file:199][file:170][file:184]