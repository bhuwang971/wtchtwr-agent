# NL-to-SQL

## Plain-English Version

For structured questions, the system turns the user’s request into DuckDB SQL, validates that SQL, repairs common mistakes, executes it, and only then uses the results to build a natural-language answer.

That is much safer than “ask the model for the answer directly,” because the model is forced to go through the database.

Repo anchors:

- main SQL pipeline: [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)
- route into SQL: [`agent/graph.py::_plan_to_sql_node`](../../agent/graph.py)
- planner choosing SQL policy: [`agent/policy.py::plan_steps`](../../agent/policy.py)

## Where The SQL Path Begins

The SQL path is chosen in [`agent/policy.py::plan_steps`](../../agent/policy.py), then executed by [`agent/graph.py::_plan_to_sql_node`](../../agent/graph.py), which calls [`agent/nl2sql_llm.py::plan_to_sql_llm`](../../agent/nl2sql_llm.py).

Common policies include:

- `SQL_HIGHBURY`
- `SQL_MARKET`
- `SQL_COMPARE`

These depend on intent and scope produced earlier in the graph.

## How Schema Grounding Is Done

The most important grounding artifact is `SCHEMA_BLOCK` in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py).

That block explicitly lists tables such as:

- `listings_cleaned`
- `highbury_listings`
- `amenities_norm`

It also encodes business semantics, for example:

- `neighbourhood_group` means borough
- occupancy fields are future occupancy projections
- revenue fields are estimated revenue in USD
- avoid using `is_highbury` where the column does not exist

Why this matters:

- the model is not expected to infer schema from memory
- the prompt gives both table names and domain meaning

## How The Prompt Is Built

[`agent/nl2sql_llm.py::build_prompt`](../../agent/nl2sql_llm.py) combines:

- schema block
- SQL guidelines
- current user query
- normalized filter hints

The prompt is aimed at DuckDB SQL specifically, not generic ANSI SQL.

Likely design reason:

- pragmatic and easy to inspect
- tailored to the repo’s actual schema
- lightweight compared with planner-heavy systems

## How SQL Is Generated

`plan_to_sql_llm(...)` in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py):

1. skips non-SQL conversational intents
2. builds the prompt
3. streams SQL from the model with `_stream_sql(...)`
4. rejects obviously unsafe/non-SELECT SQL
5. validates and repairs the SQL
6. executes the query
7. writes structured SQL output into `state.sql`

Model defaults in the repo:

- primary default: `gpt-4o-mini`
- fallback default: `gpt-4o`
- repair default: `gpt-4o-mini`

These are configurable via env vars in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py) and [`agent/config.py`](../../agent/config.py).

## SQL Cleaning Before Execution

Before validation/execution, [`agent/nl2sql_llm.py::clean_sql_before_execute`](../../agent/nl2sql_llm.py) strips or normalizes known bad patterns, including problematic `is_highbury` usage.

Why this exists:

- some model errors are common enough that deterministic cleanup is cheaper than an LLM retry

## SQL Verification

The first hard safeguard is [`agent/nl2sql_llm.py::verify_sql`](../../agent/nl2sql_llm.py), which runs DuckDB `EXPLAIN`.

If `EXPLAIN` works, the SQL is considered syntactically and structurally valid enough to execute.

What it catches:

- malformed SQL
- missing tables
- missing columns
- parser errors

What it does **not** catch:

- semantic correctness
- wrong aggregation or wrong table choice

## SQL Repair Loop

If verification fails, [`agent/nl2sql_llm.py::verify_and_repair_sql`](../../agent/nl2sql_llm.py) tries:

1. `_repair_sql_rule_based(...)`
2. `_repair_sql_with_llm(...)`

### Rule-based repair

Used for predictable issues:

- known invalid patterns
- minor syntax cleanup
- repeated bad clauses

### LLM repair

Used when rule-based repair cannot recover the query.

Why this design likely exists:

- deterministic repair is cheaper and easier to trust
- LLM repair is reserved for harder cases

## SQL Execution

Execution happens in [`agent/nl2sql_llm.py::execute_duckdb`](../../agent/nl2sql_llm.py).

That function:

- opens DuckDB
- executes the SQL
- fetches results into a DataFrame
- returns a normalized result containing:
  - rows
  - columns
  - summary
  - markdown table
  - aggregates / helper fields when available

If no rows are returned, the summary becomes:

- `"No records found for this query."`

## Result Formatting

User-facing formatting is handled by helpers like:

- `format_sql_summary(...)`
- `summarise_table_overview(...)`
- `_summarize_result(...)`

The graph stores SQL output in `state.sql`, and later composition turns that structured output into final prose.

## How Hallucinated SQL Is Reduced

This repo reduces SQL hallucinations through multiple layers:

1. explicit schema block
2. prompt instructions tied to specific tables and business semantics
3. SQL cleaning
4. `EXPLAIN` validation
5. deterministic repair
6. optional LLM repair
7. final answer composition from actual query results

## Exact Safeguards

| Safeguard | Repo location | What it protects against |
| --- | --- | --- |
| schema grounding | `SCHEMA_BLOCK` in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py) | invented schema |
| SQL cleaning | `clean_sql_before_execute(...)` | common invalid clauses |
| syntax verification | `verify_sql(...)` | parser/plan failures |
| deterministic repair | `_repair_sql_rule_based(...)` | recurring known issues |
| LLM repair | `_repair_sql_with_llm(...)` | harder SQL failures |
| execution through DuckDB | `execute_duckdb(...)` | ties final answer to actual rows |

## Where The Design Is Strong

- grounded in explicit schema
- verification before execution
- repair loop instead of simple fail-fast
- local DuckDB makes generated SQL easy to inspect
- benchmark framework can assert `require_sql`, `sql_contains`, and `min_rows`

## Weaknesses / Risks

- `EXPLAIN` proves parseability, not business correctness
- design is still prompt-based, not logical-plan-first
- valid SQL can still answer the wrong business question
- the repo still shows evidence of parser warnings in some benchmark runs even when end-to-end cases pass

## Why This Repo Likely Chose This Design

### Chosen approach

- prompt the LLM with explicit schema
- validate and repair
- run on local DuckDB

### Likely reasons

- easy to implement
- easy to demo
- easy to debug
- works well for laptop-scale analytics

## Alternatives That Could Have Been Used

| Alternative | Why it might help | Why this repo probably did not choose it |
| --- | --- | --- |
| template-based SQL generation | safer for fixed queries | too rigid for open-ended analytics |
| logical-plan-first generation | better semantic control | more engineering overhead |
| schema retrieval / semantic column linking | scales better to larger schemas | schema here is still small enough to inline |
| hosted warehouse + query service | more production-ready | worse local portability/demo ergonomics |
| LangChain SQL chains | more batteries included | this repo appears to prefer direct control |

## What I Would Improve Next

1. add a logical planning stage before SQL emission
2. maintain a golden SQL set for critical business questions
3. add semantic correctness checks, not just syntax checks
4. show SQL explanation in the UI: why this table, why this filter, why this aggregation
5. add query complexity guards for very broad scans

## Interviewer May Ask

### “How do you stop the model inventing columns?”

By constraining the prompt with the project schema, validating with `EXPLAIN`, cleaning common bad patterns, and repairing invalid queries before execution.

### “What is the biggest remaining NL-to-SQL risk?”

Semantically plausible but wrong SQL. The query can be valid and still answer the wrong business question.

