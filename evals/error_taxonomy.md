# Error Taxonomy

Use this taxonomy when reviewing failed benchmark cases or manually grading answers.

## Core error classes

- `routing_error`
  - wrong intent, scope, or policy selected
- `filter_extraction_error`
  - borough, neighborhood, date, listing, KPI, or sentiment constraints resolved incorrectly
- `sql_generation_error`
  - malformed SQL, wrong table, wrong aggregation, or unsafe SQL shape
- `retrieval_miss`
  - relevant review evidence existed but was not retrieved or surfaced
- `synthesis_hallucination`
  - final answer claimed more than the SQL rows or citations support
- `abstention_failure`
  - system should have abstained or lowered confidence, but answered as if evidence were strong
- `tool_disagreement`
  - SQL and RAG pointed in different directions and the answer failed to reconcile that conflict

## Review guidance

For every failed benchmark or manual review:

1. assign one primary error class
2. assign optional secondary classes
3. write a one-line fix hypothesis

That makes the project much easier to discuss in an interview because it shows you diagnose failures systematically rather than just eyeballing pass/fail counts.
