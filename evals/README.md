# wtchtwr Evaluation Framework

This folder contains a lightweight benchmark/evaluation harness for checking response accuracy over time.

## Files

- `benchmarks.sample.json`: starter benchmark cases you can copy and extend
- `benchmarks.local.json`: your main tuned regression pack
- `benchmarks.holdout.json`: separate holdout/adversarial pack for paraphrases, multi-clause prompts, and constraint-following checks
- `benchmarks.adversarial.json`: explicit stress pack for contradictory prompts, vague business phrasing, unsupported slices, and weak-evidence handling
- `benchmarks.blind.sample.json`: starter blind pack template you should keep separate from daily tuning
- `review_sheet.template.csv`: human-labeled answer review template
- `error_taxonomy.md`: shared labels for benchmark failure analysis
- `runner.py`: benchmark execution and scoring logic
- `interview_summary.py`: interview-ready rollups from benchmark output

## What it checks

Each benchmark case can assert:

- `intent`
- `policy`
- `scope`
- `filters_subset`
- `sql_contains`
- `answer_contains`
- `require_sql`
- `min_rows`
- `max_rows`
- `min_rag_snippets`
- `field_equals`
- `require_abstain`

You can also add `manual_checks` notes for human review.

## Run it

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.sample.json
```

This writes:

- `evals\reports\benchmark-report-<timestamp>.json`
- `evals\reports\benchmark-report-<timestamp>.md`
- `evals\reports\interview-metrics-latest.json`
- `evals\reports\interview-metrics-latest.md`
- `evals\reports\interview-metrics-<pack>-latest.json`
- `evals\reports\interview-metrics-<pack>-latest.md`

The runner now performs a readiness precheck before execution. If your selected cases include retrieval-backed categories
(`rag`, `hybrid`, or `triage`) and Qdrant is unavailable, the run exits early instead of producing misleading `0%` scores.

## Suggested workflow

1. Start with `benchmarks.local.json` for your working benchmark pack
2. Keep `benchmarks.holdout.json` separate so it reflects prompts you did not explicitly tune against
3. Add or refine questions you care about
4. For each case, define expected route/filter/SQL behavior
5. Re-run after code changes
6. Compare reports over time

Recommended daily command:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.local.json
```

Holdout/adversarial run:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.holdout.json
```

Explicit adversarial run:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.adversarial.json
```

Examples of pack-specific summaries after running:

- `interview-metrics-local-latest.md`
- `interview-metrics-holdout-latest.md`

If Qdrant is not up, start it first:

```powershell
docker start wtchtwr-qdrant
```

If you want to regenerate the interview summary from an existing benchmark report:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\interview_metrics.py
```

If you want to compare multiple model setups on the same benchmark pack:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\compare_benchmark_models.py `
  --benchmark-file evals\benchmarks.local.json `
  --model baseline:gpt-5.1:gpt-4o-mini `
  --model fast:gpt-4o:gpt-4o-mini
```

Model syntax:

- `label:main_model`
- `label:main_model:nl2sql_model`
- `label:main_model:nl2sql_model:main_fallback:nl2sql_fallback`

Single-model benchmark runs can also override models directly:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py `
  --benchmark-file evals\benchmarks.local.json `
  --label gpt51 `
  --model gpt-5.1 `
  --nl2sql-model gpt-4o-mini
```

## Example case

```json
{
  "id": "highbury-market-sql-shape",
  "query": "List our Highbury listings in Manhattan with prices",
  "tenant": "highbury",
  "composer_enabled": false,
  "expected": {
    "policy": "SQL_HIGHBURY",
    "require_sql": true,
    "filters_subset": {
      "borough": ["Manhattan"]
    },
    "sql_contains": ["highbury_listings"],
    "min_rows": 1
  },
  "manual_checks": [
    "Confirm the listed rows are actually Highbury-managed units."
  ]
}
```

## Notes

- Start with `composer_enabled: false` when you want to validate routing, filters, SQL shape, and grounding without extra LLM phrasing variability.
- Use manual review for cases where business correctness matters more than exact string matching.
- Treat this as a benchmark harness, not a replacement for unit tests.
- Use `interview-metrics-latest.md` as the fast summary for interview prep. It distills overall accuracy, latency, strongest categories, weakest categories, and the slowest benchmark cases into talking points.
- Keep the tuned regression pack and the holdout/adversarial pack separate. If both rise together, you have stronger evidence that the system is improving rather than just overfitting to the benchmark wording.
- The app now exposes an `AI Metrics` page in the frontend, backed by `/api/ai/metrics`, so you can demo health checks, tuned/holdout metrics, and category-level quality without leaving the product.
