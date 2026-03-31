# Backend And Storage

## Backend Framework

The backend is a FastAPI service defined in [`backend/main.py`](../../backend/main.py).

Core responsibilities:

- conversation APIs
- streaming chat responses
- summary/email flows
- exports
- dashboard endpoints (via router)
- data explorer endpoints
- health/readiness endpoints
- AI metrics endpoint
- Slack startup/status hooks

## API Surface

Important endpoint groups in [`backend/main.py`](../../backend/main.py) and [`backend/dashboard_router.py`](../../backend/dashboard_router.py):

### Conversations

- `GET /api/conversations`
- `POST /api/conversations`
- `PATCH /api/conversations/{conversation_id}`
- `GET /api/conversations/{conversation_id}`
- `POST /api/conversations/{conversation_id}/messages`
- `DELETE /api/conversations/{conversation_id}`
- `DELETE /api/conversations/{conversation_id}/messages/{message_id}`

### Summary / email

- `POST /api/conversations/{conversation_id}/summary`
- `POST /api/conversations/{conversation_id}/summary/email`

### Export

- `POST /api/conversations/{conversation_id}/messages/{message_id}/export`
- `GET /api/exports/{token}`

### Data explorer

- `GET /api/data-explorer/schema`
- `POST /api/data-explorer/query`
- `POST /api/data-explorer/export`
- `GET /api/data-explorer/column-values/{table}/{column}`

### Dashboard

- `GET /api/dashboard/meta`
- `GET /api/dashboard/filters`
- `POST /api/dashboard/insights`
- `POST /api/dashboard/view`

### Health and metrics

- `GET /api/health/live`
- `GET /api/health/ready`
- `GET /api/health/status`
- `GET /api/ai/metrics`

### Slack

- `POST /api/slackbot/start`
- `GET /api/slackbot/status`

## Request / Response Flow

The main chat path is:

1. [`backend/main.py::post_message`](../../backend/main.py) receives the request
2. `_record_user_message(...)` persists the user message
3. `_execute_langgraph(...)` or `_stream_response(...)` runs the orchestrator
4. `_finalize_assistant_message(...)` shapes and persists the assistant message
5. the updated conversation is returned to the UI

This is a classic API shell around a deeper orchestration layer.

## Conversation Storage

The backend stores chat state in DuckDB tables created by [`backend/main.py::ensure_schema`](../../backend/main.py):

- `conversations`
- `messages`
- `exports_cache`
- `thread_map`

Message rows include:

- `id`
- `conversation_id`
- `role`
- `content`
- `nl_summary`
- `payload`
- `timestamp`

This is important because the backend persists not only text, but structured assistant payloads.

## Thread Mapping

Thread mapping is handled by:

- [`backend/main.py::ensure_thread_map`](../../backend/main.py)
- [`backend/main.py::map_thread_to_conversation`](../../backend/main.py)

This maps a thread key to the conversation ID so graph memory and frontend conversation identity stay aligned.

## Streaming Vs Synchronous Modes

### Streaming

Implemented by [`backend/main.py::_stream_response`](../../backend/main.py).

What it does:

- calls `stream_agent(...)`
- converts agent outputs into SSE-style events
- suppresses SQL leakage in token output
- captures the final payload
- still persists the final assistant message at the end

### Synchronous

Implemented by [`backend/main.py::_execute_langgraph`](../../backend/main.py).

What it does:

- calls `run_agent(...)`
- normalizes telemetry and latency
- returns the completed result object

Why both exist:

- streaming gives better UX
- sync is simpler for scripts, tests, and some internal flows

## Assistant Payload Construction

The most important backend payload function is [`backend/main.py::build_assistant_payload`](../../backend/main.py).

It determines:

- response type (`sql`, `rag`, `hybrid`, `expansion`, `text`)
- table payloads
- summary
- row count
- duration
- rag snippets
- aggregates
- policy
- markdown table
- sentiment analytics
- confidence
- trace
- abstention flag

This payload is what the frontend actually consumes and what gets persisted with the message.

## Confidence / Trace / Observability

Observability logic lives in [`backend/ai_observability.py`](../../backend/ai_observability.py).

Important functions:

- `build_confidence_payload(...)`
- `build_trace_payload(...)`
- `load_ai_metrics_payload(...)`

These functions power:

- chat answer confidence
- AI trace panel
- AI metrics page

## Health And Readiness Endpoints

Health functions in [`backend/main.py`](../../backend/main.py) check dependencies such as:

- DuckDB
- Qdrant
- OpenAI configuration
- Tavily configuration
- email configuration

Why this matters:

- the repo explicitly distinguishes infra readiness from model quality

## Summary / Email Flow

Conversation summaries are built in:

- [`backend/main.py::_build_conversation_summary`](../../backend/main.py)
- `_build_concise_summary(...)`
- `_build_detailed_summary(...)`

Email sending is handled by:

- [`backend/emailer.py::send_email`](../../backend/emailer.py)

Why this exists:

- summaries make the product feel more like a workflow assistant than a one-shot chatbot

## Export Flow

Conversation export:

- [`backend/main.py::api_export_message`](../../backend/main.py)

Data Explorer export:

- [`backend/main.py::api_data_explorer_export`](../../backend/main.py)

Small exports use:

- [`backend/exporter.py::stage_csv`](../../backend/exporter.py)

Large exports can fall back to:

- ZIP handling in `main.py`
- Google Drive upload via [`backend/gdrive.py::DriveUploader`](../../backend/gdrive.py)

## Dashboard Backend

Dashboard logic lives in:

- [`backend/dashboard.py`](../../backend/dashboard.py)
- exposed through [`backend/dashboard_router.py`](../../backend/dashboard_router.py)

Important design choice:

- dashboard features are cached into a parquet file at `data/cache/dashboard_features.parquet`
- the dashboard reads that cache rather than recomputing joins on every request

## Data Layer

### Structured data storage

The structured analytics layer centers on:

- [`db/airbnb.duckdb`](../../db/airbnb.duckdb)
- clean parquet files in [`data/clean/`](../../data/clean)

Important consumers:

- [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)
- [`backend/dashboard.py`](../../backend/dashboard.py)
- [`backend/data_explorer.py`](../../backend/data_explorer.py)

### Vector data storage

The vector retrieval layer uses:

- Qdrant for online vector search
- embeddings/metadata artifacts in [`vec/airbnb_reviews/`](../../vec/airbnb_reviews)

Build path:

- [`scripts/rebuild_review_vectors.py`](../../scripts/rebuild_review_vectors.py)

### Metadata

Review metadata includes:

- listing ID
- comment ID
- borough
- neighborhood
- month
- year
- `is_highbury`
- sentiment scores / label

That metadata is what makes the retrieval layer usable for analytics-style filtering rather than generic semantic search.

### Data contracts and trust

Trust tooling lives in:

- [`backend/data_trust.py`](../../backend/data_trust.py)
- [`scripts/data_quality_report.py`](../../scripts/data_quality_report.py)
- [`docs/data_dictionary.md`](../data_dictionary.md)
- [`docs/data_lineage.md`](../data_lineage.md)

`backend/data_trust.py` validates:

- required DuckDB table columns
- required parquet file columns
- duplicate listing IDs
- invalid coordinates
- impossible prices
- inconsistent borough labels
- review duplicate/null-rate issues

### Freshness assumptions

This repo does not show a full continuously running ingestion pipeline. It assumes:

- parquet inputs are refreshed offline
- vector artifacts are rebuilt when needed via script
- dashboard feature cache can be regenerated from DuckDB/parquet

That is appropriate for a portfolio project, but it is worth stating clearly in interviews.

## Data Explorer Backend

Data Explorer logic lives in [`backend/data_explorer.py`](../../backend/data_explorer.py).

Important design choices:

- safe-list of exposable tables and join keys
- structured query construction rather than arbitrary user SQL
- freeform query helper exists, but the main path is structured query building

That is a good safety choice for a demo/analytics app.

## Slack Integration

Slack bot lifecycle is bootstrapped from [`backend/main.py::_start_slack_bot_thread`](../../backend/main.py), but the actual bot logic lives in [`agent/slack/bot.py`](../../agent/slack/bot.py).

Important point:

- the Slack bot reuses the same backend conversation API path rather than inventing a separate inference stack

## Startup / Background Behavior

On startup, [`backend/main.py::startup_event`](../../backend/main.py):

- ensures schema exists
- purges expired exports
- starts the Slack bot thread
- starts a warmup thread

Warmup behavior in [`backend/main.py::_run_warmup_tasks`](../../backend/main.py):

- graph compilation
- vector readiness
- DuckDB warmup
- sample agent prompts

This is not a scheduler system. It is a startup warmup sequence.

## Persistence Tech Debt To Admit

[`backend/storage.py`](../../backend/storage.py) still exists and looks like older JSON/file-based persistence logic. The current web app path uses DuckDB-backed storage in [`backend/main.py`](../../backend/main.py).

Good interview phrasing:

- “There is a legacy storage module still in the repo, but the active path for the current app uses DuckDB conversation tables in `backend/main.py`.”

## Strong Backend Choices

- thin API shell over a more structured agent layer
- durable message persistence
- streaming and sync both supported
- health/readiness separation
- structured exports and email flows

## Weak Spots To Admit

- `backend/main.py` is very large and owns many concerns
- there is legacy storage code alongside current storage
- some startup and debug logging is clearly demo/hardening oriented rather than polished production observability
