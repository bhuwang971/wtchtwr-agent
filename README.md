# wtchtwr

`wtchtwr` is an AI-native decision-support copilot for short-term rental portfolio analysis. It combines deterministic analytics, retrieval over review data, and agentic orchestration to help operators answer business questions about pricing, occupancy, revenue, guest feedback, portfolio triage, and expansion strategy.

This repository now reflects the current project state in `bhuwang971/wtchtwr-agent`, including local data assets, benchmark/evaluation tooling, health checks, interview metrics, and observability features in the UI.

## What the product does

- Natural-language analytics over Airbnb portfolio and market data
- SQL-backed answers for structured metrics like pricing, occupancy, and revenue
- RAG-backed answers for review themes, complaints, and sentiment evidence
- Hybrid answers that combine SQL and review evidence in one response
- Portfolio triage for identifying weak performers and optimization opportunities
- Expansion scouting for new neighborhood and market opportunities
- Dashboard and data explorer surfaces for self-serve analysis

## Business value

This project is easiest to explain as a decision-support copilot for operations, portfolio management, and expansion.

- Faster access to portfolio insights
  - operators can ask questions instead of writing SQL
- Better portfolio decisions
  - compare Highbury listings against the surrounding market on pricing, occupancy, and revenue
- Faster problem detection
  - identify underperforming listings and guest pain points from reviews
- Better growth strategy
  - evaluate where to expand next using market and review signals
- Reduced analyst dependency
  - non-technical users can self-serve common questions

## Architecture

### Core components

- `agent/`
  - intent classification
  - planning and routing
  - NL-to-SQL generation
  - retrieval and reranking
  - synthesis and composition
- `backend/`
  - FastAPI API layer
  - health and readiness endpoints
  - conversation persistence
  - dashboard and data explorer APIs
  - observability payloads for UI and evaluation
- `frontend/`
  - chat UI
  - dashboard
  - data explorer
  - AI metrics page
  - AI trace and confidence surfaces
- `evals/`
  - tuned regression pack
  - holdout pack
  - interview summaries
  - model comparison reports
- `db/`, `data/`, `vec/`
  - DuckDB analytics database
  - cleaned parquet datasets
  - review embedding assets and metadata

### System thinking

This project is intentionally designed as an agentic system rather than a single chatbot call.

- Constrain the agent
  - route work into deterministic SQL, retrieval, dashboard, and expansion paths
- Ground the answer
  - structured truth comes from DuckDB
  - unstructured evidence comes from Qdrant-backed review retrieval
- Verify intermediate steps
  - SQL verification and repair loop before execution
  - retrieval reranking and weak-evidence detection
- Measure continuously
  - benchmark packs
  - category-level accuracy
  - latency tracking
- Fail gracefully
  - health checks
  - readiness checks
  - degraded-mode signals when retrieval is unavailable or evidence is sparse

## Guardrails and observability

The current build includes several guardrails and interview-friendly observability features.

- Health endpoints
  - `GET /api/health/live`
  - `GET /api/health/ready`
  - `GET /api/health/status`
- AI metrics endpoint
  - `GET /api/ai/metrics`
- SQL verifier and repair loop
  - validates generated SQL before execution
  - attempts repair on common failures
- Retrieval grounding
  - reranker over retrieved review snippets
  - weak-evidence detection
- Confidence scoring
  - answer confidence
  - SQL confidence
  - retrieval confidence
- AI trace panel in the chat UI
  - intent
  - scope
  - policy
  - resolved filters
  - SQL path
  - retrieval path
  - token usage
  - latency and degraded signals

## Evaluation discipline

The repo includes separate benchmark sets so accuracy claims are grounded in repeatable evaluation.

- `evals/benchmarks.local.json`
  - tuned regression pack for the main supported behaviors
- `evals/benchmarks.holdout.json`
  - holdout pack for generalization beyond the tuned set
- `evals/reports/`
  - benchmark reports
  - interview metrics
  - model comparison reports

Metrics tracked include:

- overall accuracy
- SQL accuracy
- RAG accuracy
- hybrid accuracy
- assertion-level accuracy
- P50 and P95 latency
- strongest and weakest categories
- failed case IDs and regressions

## Interview-facing features

If you are presenting this project in an interview, these are the strongest differentiators now in the repo.

- AI trace/debug panel in the UI
  - shows how the system routed and grounded each answer
- Confidence scoring
  - makes answer quality visible instead of implicit
- Benchmark dashboard
  - tuned and holdout results available through the AI metrics page
- Holdout evaluation
  - demonstrates awareness of overfitting to a curated regression pack
- Health and readiness checks
  - shows operational thinking
- SQL repair and retrieval reranking
  - shows practical reliability improvements rather than only prompt tweaks

## Local setup

### Prerequisites

- Python 3.11
- Node.js 18+
- Docker Desktop

### Required local assets

These files are expected in the repo:

- `db/airbnb.duckdb`
- `data/clean/listings_cleaned.parquet`
- `data/clean/highbury_listings.parquet`
- `data/clean/review_sentiment_scores.parquet`
- `data/clean/reviews_enriched.parquet`
- `vec/airbnb_reviews/reviews_embeddings.npy`
- `vec/airbnb_reviews/reviews_metadata.parquet`

### Environment

Copy `.env.example` to `.env` and set at minimum:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

MAIL_HOST=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=true
MAIL_USE_TLS=false
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM="wtchtwr <yourgmail@gmail.com>"
```

Slack and Google Drive variables can be left blank if you are not using those integrations.

## Daily startup

### 1. Start Docker Desktop

Wait until Docker is fully running.

### 2. Start Qdrant

First time:

```powershell
docker run -d --name wtchtwr-qdrant -p 6333:6333 qdrant/qdrant
```

Normal usage:

```powershell
docker start wtchtwr-qdrant
```

### 3. Start the backend

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

### 4. Start the frontend

```powershell
cd C:\Users\bhuwa\wtchtwr\frontend
npm.cmd run dev
```

### 5. Open the app

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- AI metrics: `http://localhost:5173/ai-metrics`

## Running evaluations

### Tuned regression pack

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.local.json
```

### Holdout pack

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.holdout.json
```

### Model comparison

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\compare_benchmark_models.py `
  --benchmark-file evals\benchmarks.local.json `
  --model gpt51:gpt-5.1:gpt-4o-mini `
  --model gpt4o:gpt-4o:gpt-4o-mini `
  --model gpt4omini:gpt-4o-mini:gpt-4o-mini
```

## Useful endpoints

- `GET /api/health/live`
- `GET /api/health/ready`
- `GET /api/health/status`
- `GET /api/ai/metrics`
- `GET /api/dashboard/filters`
- `POST /api/dashboard/view`
- `GET /api/data-explorer/schema`
- `POST /api/data-explorer/query`

## Repo layout

```text
wtchtwr/
├── agent/
├── backend/
├── frontend/
├── db/
├── data/
├── evals/
├── scripts/
├── tests/
├── vec/
└── README.md
```

## Best-practice talking points for agentic AI

If you are asked about best practices for agentic systems, this project gives you concrete examples of each.

- Constrain the agent with deterministic tools instead of letting the LLM do everything
- Ground answers in SQL and retrieval evidence
- Verify intermediate steps before presenting a result
- Measure quality with regression and holdout benchmark packs
- Track latency and failure modes, not just accuracy
- Surface confidence and traceability to users
- Design for degraded mode and weak-evidence cases
- Keep humans in the loop for high-stakes interpretation

## Project status

This repository is set up for interview demos, technical walkthroughs, and portfolio presentation. It is not positioned as a hardened production deployment, but it demonstrates the core engineering patterns that matter for modern AI and agentic systems:

- orchestration
- grounding
- guardrails
- observability
- evaluation
- business alignment

## Ownership

Current repository: `https://github.com/bhuwang971/wtchtwr-agent`
