# Hybrid Local RAG + Cloud LLM Architecture for a Sovereign AI Data Analyst (Small Business)

## 1. Purpose and Design Goals

This architecture describes a **hybrid Sovereign AI RAG Data Analyst** for small businesses:

- All **business data, documents, and logs** stay on the client’s infrastructure (local servers or private cloud).
- A **local RAG pipeline** (vector store + local LLM) handles sensitive queries and everyday analysis.[web:107][web:108]
- Optional **cloud LLM APIs** are used for higher‑end reasoning or generative tasks that can safely operate on *processed* or anonymized data.[web:106][web:115]
- The suite is delivered as a deployable package; the client installs it locally, adds their data sources and **API keys**, and is ready to ask questions.

This reflects current sovereign AI RAG practice, where local LLMs + RAG are combined with cloud capabilities in a controlled way.[web:106][web:107][web:93][web:115]

---

## 2. High-Level Architecture Overview

At a high level, the system consists of six layers:

1. **Local Data & Document Layer** – client’s databases, files, and object storage.
2. **Local RAG Layer** – ingestion, chunking, embeddings, vector store, and retrieval.
3. **Local LLM Layer** – self‑hosted LLM runtime for sovereign inference.
4. **Cloud LLM Layer** – optional external APIs for advanced reasoning.
5. **Routing & Governance Layer** – decides whether to use local or cloud models.
6. **Data Analyst App Layer** – UI and agentic workflows for business decision support.

A typical hybrid pattern is: local LLMs and RAG for sensitive operations; cloud APIs for general tasks without confidential information.[web:106][web:107][web:115]

---

## 3. Layer 1 – Local Data & Document Layer

### 3.1 Data Sources

Small businesses usually have:

- Operational DBs (PostgreSQL/MySQL), spreadsheets, accounting systems.
- File shares (PDF invoices, contracts, reports), emails, CRM exports.
- Optional SaaS exports (Stripe, Shopify, ERP) periodically copied to local storage.

### 3.2 Local Storage

Use local or private‑cloud storage:

- **Relational DB** (PostgreSQL recommended for structure + vector support).[web:108]
- **File/Object storage** (NAS, S3‑compatible bucket, private cloud storage) for documents.[web:101]

Document repositories are continuously watched by a **local ingestion pipeline**.[web:107][web:101]

---

## 4. Layer 2 – Local RAG Layer

This layer transforms documents + data into a searchable knowledge base.

### 4.1 Ingestion & Preprocessing

Following enterprise/local RAG patterns:[web:107][web:108][web:101]

- Watch document sources (network drives, S3 buckets, DB tables) for changes.
- For each document:
  - Extract text (PDF/Office parsing, OCR if needed).
  - Clean and normalize content (remove boilerplate, fix encoding).
  - Chunk into segments (e.g., 500–1000 characters with overlap).[web:108][web:101]
  - Generate embeddings using a local embedding model or client‑owned cloud embedding API.[web:107][web:113]

### 4.2 Vector Store and Metadata

Use **PostgreSQL + pgvector** (or similar) as the local vector store:[web:108][web:101]

- Table `rag_documents`:
  - `id`, `content`, `metadata` (source, type, date, tags),
  - `embedding` (vector column).
- Index: HNSW or IVF for fast similarity search.
- Metadata filters for tenant, user permissions, time windows.

This mirrors the OVHcloud+n8n reference where Markdown documents are embedded and stored in a PostgreSQL pgvector table, under full client control.[web:110][web:101]

### 4.3 Local Query Engine

When a user asks a question:

- Convert question to embedding.
- Perform similarity search and optional BM25 keyword search.
- Apply filters (e.g., only this client’s documents, last 12 months).
- Rerank results using relevance scoring.
- Return top‑k chunks as **local context pack**.[web:107][web:108][web:101]

---

## 5. Layer 3 – Local LLM Layer (Sovereign Inference)

This layer provides **local model inference** without leaving the client’s infrastructure.

### 5.1 Runtime Options

Use self‑hosted runtimes such as:

- **Ollama** – simple local LLM runner ideal for daily use and prototyping.[web:108][web:96][web:102]
- **vLLM** – high‑performance OpenAI‑compatible server for production serving.[web:93][web:94][web:111]
- Other local stacks (LocalAI, Qwen, Llama, etc.) depending on hardware.[web:93][web:99][web:112]

These runtimes expose HTTP APIs that your RAG server can call from inside the local network.

### 5.2 Local Answer Generation

For sensitive questions:

- The RAG server assembles prompt = user question + retrieved chunks.
- Sends prompt to local LLM endpoint (Ollama/vLLM).
- Local LLM returns an answer, which is post‑processed:
  - citation insertion,
  - formatting,
  - optional guardrail checks.[web:94][web:108]

This path ensures **no sensitive content** ever leaves the client environment.

---

## 6. Layer 4 – Cloud LLM Layer (Optional)

For tasks that benefit from frontier models and do **not require raw sensitive data**, use cloud providers via client‑owned API keys.

Examples:

- GPT‑4.x / GPT‑4.1 series (OpenAI).
- Claude Opus/Sonnet (Anthropic).
- Gemini Pro (Google).
- Region‑specific providers via OpenAI‑compatible endpoints.[web:113][web:111]

Hybrid sovereign AI approaches explicitly recommend combining sovereign infrastructure with public cloud for speed and advanced capabilities, under clear policy rules.[web:115][web:106]

---

## 7. Layer 5 – Routing & Governance Layer

This layer decides **when to use local vs cloud LLMs**, and enforces sovereignty.

### 7.1 Routing Policies

Examples of routing rules:

- **Local‑only**:
  - Queries involving raw transactional data, PII, financial details, medical info.
  - Any prompt containing “customer”, “patient”, “salary”, or similar sensitive markers.
- **Hybrid / Cloud**:
  - Non‑sensitive tasks: generic planning, copywriting, industry Q&A, template generation.
  - Summaries of already anonymized metrics (e.g., “Explain what this KPI means in plain language” using just aggregated values, not identities).

Enterprise RAG guidance suggests that local RAG handle “proprietary & sensitive” workloads, while cloud APIs cover “general‑purpose tasks with no confidential information.”[web:106][web:107]

### 7.2 Governance and Guards

Add guard mechanisms:

- **LLM Guard / safety endpoint** before cloud calls:
  - classify prompts and block unsafe ones.[web:110]
- Mask or aggregate sensitive fields before sending to cloud LLMs.
- Log all routing decisions and external requests for audits.[web:100][web:103][web:110]

OVHcloud+n8n’s sovereign RAG architecture demonstrates using a Llama‑Guard endpoint ahead of an AI Agent node to enforce safety on every request.[web:110]

---

## 8. Layer 6 – Data Analyst App and Workflows

This is the interface small‑business users see.

### 8.1 Analyst UI

Features:

- Question box + filters (time range, dataset, KPI).
- Output sections:
  - **Summary** (decision‑ready answer).
  - **Evidence & citations** (links to local documents and data views).
  - **Drivers & root causes** (analytical detail).
  - **Recommended actions** (next steps).[web:107][web:106]

The app talks to the **RAG server**, which in turn orchestrates local retrieval and local/cloud LLM calls.

### 8.2 Agentic Workflow Engine

Option 1: **n8n** workflows (visual automation).[web:101][web:116][web:118]

- Nodes for:
  - document ingestion,
  - embeddings,
  - Postgres vector store,
  - local LLM endpoints,
  - cloud LLM endpoints,
  - guardrail nodes,
  - business logic (alerts, reporting).
- n8n reference architectures show end‑to‑end RAG pipelines where:
  - ingestion and embedding are fully automated,
  - a chat trigger node retrieves from Postgres and calls an AI Agent node.[web:110][web:101]

Option 2: **LangGraph / PydanticAI** agent graphs.

- Planner node decides workflow steps.
- Retriever node calls vector store.
- Generator nodes call local or cloud LLM based on routing policy.[web:108][web:102]

---

## 9. End-to-End Request Flow (Hybrid Mode)

For a typical small‑business question, e.g., “Why did our monthly revenue drop in May and what should we do?”:

1. **User submits question** via the Data Analyst app.
2. **Routing layer classifies** the query as business analytics on proprietary data → route to **local RAG**.
3. **Local retrieval**:
   - query engine embeds question,
   - searches Postgres pgvector for relevant docs (reports, invoices, notes).[web:107][web:108][web:101]
4. **Local analytics** (optional):
   - compute metrics (e.g., revenue by month, segment changes) using local DB.
5. **Local LLM answer**:
   - RAG server sends metrics + retrieved context to local LLM (Ollama/vLLM),
   - model returns a grounded explanation and recommendations.[web:94][web:108]
6. **Optional cloud refinement** (non‑sensitive):
   - the system may send a **sanitized summary** (e.g., “revenue dropped from X to Y, key driver categories A/B/C”) to a cloud LLM for stylistic polishing or strategy framing if policy allows.[web:106][web:115]
   - no raw customer data or documents are sent.
7. **Response delivered**:
   - app shows answer + evidence,
   - user can drill down into local data and documents.

For purely generic questions (e.g., “Write a template email to notify customers of a price change”), step 2 may route directly to the cloud LLM, since no proprietary data is involved.

---

## 10. Deployment Patterns for Small Businesses

### 10.1 Single-Node “All-in-One” Deployment

For very small clients:

- One machine (local server or mini‑PC) runs:
  - PostgreSQL + pgvector.
  - Local LLM runtime (Ollama).
  - RAG server and n8n/agent workflows.
  - Data Analyst web app.[web:108][web:96][web:102]

This matches “secure local RAG system” guides where everything runs on a single server in the client environment.[web:108][web:99]

### 10.2 Light Hybrid with Private Cloud

For slightly larger clients:

- Local DB and LLM on a server or small cluster.
- Orchestration (n8n) and frontend running on a private cloud instance.
- Cloud LLM endpoints accessible via outbound HTTPS with strict firewall rules.[web:93][web:100][web:115]

Sovereign AI discussions recommend this “smart hybrid” pattern: sovereign compute + storage with controlled use of public cloud capabilities.[web:115][web:106]

---

## 11. Benefits for Small Businesses

- **Sovereignty and trust**: sensitive data never leaves local infrastructure; only carefully controlled aggregates or prompts reach cloud LLMs.[web:106][web:107][web:115]
- **Cost control**: local LLMs convert API OpEx to more predictable hardware CapEx for sustained usage.[web:108][web:99][web:112]
- **Flexibility**: clients can switch models (local or cloud) by changing endpoints and keys, without redesigning the architecture.[web:96][web:99][web:111]
- **Decision readiness**: the RAG Data Analyst turns raw local data + documents into grounded insights, explanations, and recommended actions, tailored for small business decisions.[web:106][web:107]
