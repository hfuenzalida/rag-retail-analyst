# 6. Map Your Architecture into Vibe Coding Workflows

_Based on your completed vibe-coding workflow answers._[file:199]

---

## 1. Core Vibe Coding Tooling

### 1.1 Primary Engines

You will standardize on two first-class tools:

- **Cursor** – your core local IDE interface for inline coding, quick edits, and file-level changes.
- **Claude Code** (or a customized Roo Code CLI) – for multi-file refactors, terminal workflows, and orchestrated tasks (tests, evals, branch management).[file:199][web:188][web:187]

### 1.2 Unified Workflow Configuration

Instead of fragmented rules per tool, you will use a **single, shared, markdown-driven workflow configuration**:

- Master rules live in:
  - `.cursor/rules/*.mdc`
  - `CLAUDE.md` (or equivalent for Claude Code).[file:199][web:148]
- These master configs encode:
  - coding standards and formatting guidelines,
  - architectural boundaries (Red/Green zones),
  - context-loading sequences and task phases.

This ensures Cursor composer panels and Claude Code CLI ingest **identical structural constraints**, regardless of interface.[file:199][web:186][web:192]

---

## 2. Task Granularity and Packets

### 2.1 Feature Slice Granularity

You enforce **feature-slice task packets**:

- Each vibe coding task corresponds to a **single feature slice**, such as:
  - “implement `get_top_drivers` end-to-end,”
  - “add driver analysis report endpoint,”
  - “wire `check_sensitivity` into routing.”[file:199]

You explicitly avoid:

- one-file-only micro-tasks (too fragmented), and
- **full vertical slices** where the agent rewrites API, models, and DB in one loop (too risky).[file:199][web:193][web:189]

### 2.2 Spec-Driven Task Derivation

All tasks must be **derived from `memory-bank/core/implementation-plan.md`**, not ad-hoc prompts:

- If you want to optimize driver analysis performance, the agent must:
  - first log a new step in `implementation-plan.md` with definition of done,
  - then execute against that isolated requirement.[file:199][web:148]
- “Prompt-hacking” directly on source trees (e.g., “optimize driver analysis” with no spec update) is disallowed.

This keeps architecture, documentation, and code tightly aligned.

---

## 3. Context Loading Rules

### 3.1 Curated Context Boundaries

You adopt a **highly curated context boundary strategy**:

- Agents are forbidden from blindly scanning the entire project root.
- For any backend task, agents must follow this sequence:[file:199][web:148]
  1. Read `memory-bank/core/agent-surface.md` – understand data structures, endpoints, and tool signatures.
  2. Read `memory-bank/core/architecture.md` – understand directory paths and module responsibilities.
  3. Pin **only** the explicit module folder being mutated (e.g., `backend/app/tools/` or `backend/app/agents/`).

### 3.2 Rules Enforcement

Rules files explicitly instruct:

- “Always read `product-spec.md`, `agent-surface.md`, `architecture.md`, and `testing-strategy.md` before touching backend code.”
- Reject requests to modify code when these foundational blueprints are not referenced or loaded.[file:199]

This reduces token overhead, protects performance on local hardware, and prevents context drift.

---

## 4. Mandatory Workflow Phases per Task

### 4.1 Five-Phase Execution Pipeline

Every vibe coding task packet must pass through **five locked phases**:[file:199][web:186][web:192]

1. **Plan / Spec Refinement**
   - Agent reads memory-bank files and asks clarifications.
   - Updates or confirms relevant `implementation-plan.md` entry.

2. **Code Generation**
   - Agent implements the feature slice in the targeted modules only.
   - Generates associated pytest tests in the same sweep.

3. **Auto-Run Tests**
   - Agent or terminal workflow automatically runs:
     - unit tests for affected tools,
     - integration tests for affected endpoints.

4. **Auto-Run Offline Eval Subset**
   - Agent triggers a subset of Pydantic Evals against golden questions relevant to the feature.
   - Must pass defined thresholds from section 5 (tests/evals).[file:184]

5. **Human Review + Commit**
   - Only after tests and evals pass does the change move to human review and commit/merge.

### 4.2 Post-Hoc Test Generation with Pre-Commit Verification

Instead of strict TDD (write failing tests first), your workflow:

- lets the agent generate code and corresponding tests **together**, then
- enforces that tests and evals **must pass** before human review or commit.[file:199]

This balances vibe coding ergonomics with strong pre-commit verification.

---

## 5. Role-Based Vibe Workflows and Zones

### 5.1 Single Architect / Product Owner Model

You optimize the system for a **highly autonomous Single Architect / Product Owner** (you), with potential future collaborators.[file:199][web:191]

### 5.2 Red Zone vs Green Zone Roles

You segment tool permissions into **Red Zone** and **Green Zone**:

- **Green Zone (High Autonomy)**:
  - Frontend UI layouts and components.
  - Data visualizations and charts.
  - Markdown documentation and ancillary content.
  - Agents can auto-generate and auto-merge once tests pass, with light review.[file:199][file:170]

- **Red Zone (Human Gatekeeper)**:
  - Prompt templates and agent configs.
  - Cloud/local routing logic and sensitivity checks.
  - Security controls and RBAC.
  - Financial/metric computations and DB schema.
  - Eval logic and golden question datasets.
  - Agents may **only propose diffs**; auto-merge is forbidden.[file:199][file:184][web:164][web:193]

You, as architect, act as **gatekeeper** for Red Zone changes.

---

## 6. Mapping Architecture Layers to Vibe Workflows

You explicitly vary autonomy level by architectural layer:[file:199][web:193]

| Layer                      | Vibe Coding Autonomy Level | Operational Boundary                                                  |
|----------------------------|----------------------------|------------------------------------------------------------------------|
| API Layer (`backend/app/api`)    | **Conservative**            | Agents can scaffold skeleton endpoints from existing models, but must not change routing parameters or security decorators without manual review. |
| Agents Layer (`backend/app/agents`) | **Single-Task Isolation**   | Only one agent framework or prompt system can be mutated per task; no multi-agent refactors in a single pass. |
| Tools Layer (`backend/app/tools`)   | **High Aggressiveness**     | Agents have full freedom to write new Python tool logic from spec, as long as tests/evals are generated and passed. |
| Memory-Bank (`memory-bank/`)        | **Propose Diffs Only**      | Agents may draft changes to `implementation-plan.md`, `progress.md`, `testing-strategy.md`, etc., but cannot overwrite tracking matrices or plans without your explicit approval. |

This mapping keeps high-churn, low-risk code (tools, UI) agent-friendly while locking down architecture-critical surfaces.

---

## 7. Critical Path and Mutation Boundaries

### 7.1 Critical Optimization Path

You prioritize the core transactional vertical loop:[file:199]

> User Question → `/query` → Sensitivity Check → Local/Cloud Routing → Structured Tool Selection → Validated Answer Panel UI.

This path is the **primary optimization target** for vibe coding.

### 7.2 Read-Only Runtime Execution for Live Models

You enforce an **absolute read-only runtime boundary** for live analytical models:

- Operational RAG analyst models must **never**:
  - modify active DB schema,
  - drop or alter tables,
  - change production configs or thresholds directly.[file:199][file:170]

If a user asks to “fix low-stock configuration values,” the analyst:

- returns a **structured recommendation object** (e.g., suggested thresholds),
- which a human admin reviews and approves via an admin dashboard before any config change is applied.[file:199]

---

## 8. Git, Branching, and Review Automation

### 8.1 One Feature Slice Per Branch

You adopt a strict **one feature slice per branch** strategy:[file:199][web:195]

- Before executing a task, the terminal agent:
  - creates a branch with standardized naming (e.g., `feature/rag-analyst-drivers`),
  - limits changes in that branch to the defined feature slice.

### 8.2 Agent-Generated Commits and PRs

Agents are allowed to automate Git ergonomics but **not** the final merge:

- Automatically:
  - create branches for tasks,
  - write conventional commit messages (e.g., `feat(tools): add driver computation logic`),
  - open draft pull requests with:
    - files changed,
    - pytest output summaries,
    - Pydantic Evals accuracy/groundedness scores.[file:199]

- You retain sole ownership of:
  - reviewing diffs,
  - confirming tests/evals,
  - merging PRs into main.

This yields high-velocity, well-documented PRs while preserving architectural control.

---

With these vibe coding workflows mapped to your architecture:

- agents move through the repo in **structured, spec-driven ways**,
- context usage is bounded and efficient,
- every change passes through tests, evals, and human gates appropriate to its risk level,
- and Git + rules files encode the workflows so you can reliably scale your vibe-coded development loop.
