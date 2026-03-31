from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterator, List, Optional, Sequence

from agent.config import load_config
from agent.graph import run as run_agent


@dataclass
class AssertionResult:
    name: str
    passed: bool
    expected: Any = None
    actual: Any = None
    detail: Optional[str] = None


@dataclass
class CaseResult:
    case_id: str
    query: str
    category: str
    passed: bool
    tags: List[str] = field(default_factory=list)
    assertions: List[AssertionResult] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class AggregateBucket:
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0


@dataclass
class LatencySummary:
    count: int = 0
    avg_s: float = 0.0
    p50_s: float = 0.0
    p95_s: float = 0.0
    max_s: float = 0.0


@dataclass
class BenchmarkSummary:
    assertion_total: int
    assertion_passed: int
    assertion_failed: int
    assertion_pass_rate: float
    category_breakdown: Dict[str, AggregateBucket]
    intent_breakdown: Dict[str, AggregateBucket]
    policy_breakdown: Dict[str, AggregateBucket]
    latency: LatencySummary
    sql_cases: int
    sql_cases_passed: int
    rag_cases: int
    rag_cases_passed: int
    hybrid_cases: int
    hybrid_cases_passed: int


@dataclass
class BenchmarkReport:
    benchmark_file: str
    generated_at: str
    model_label: str
    openai_model: Optional[str]
    openai_fallback_model: Optional[str]
    nl2sql_model: Optional[str]
    nl2sql_fallback_model: Optional[str]
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    summary: BenchmarkSummary
    results: List[CaseResult] = field(default_factory=list)


@dataclass(frozen=True)
class ModelConfig:
    label: str
    openai_model: Optional[str] = None
    openai_fallback_model: Optional[str] = None
    nl2sql_model: Optional[str] = None
    nl2sql_fallback_model: Optional[str] = None


@dataclass(frozen=True)
class ReadinessStatus:
    service: str
    ok: bool
    detail: str


def load_benchmarks(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        cases = payload.get("cases") or []
    elif isinstance(payload, list):
        cases = payload
    else:
        raise ValueError("Benchmark file must be a JSON object with 'cases' or a JSON array.")
    if not isinstance(cases, list):
        raise ValueError("Benchmark cases must be a list.")
    return cases


def _categories_requiring_qdrant(cases: Sequence[Dict[str, Any]]) -> set[str]:
    required = set()
    for case in cases:
        category = str(case.get("category") or "").lower()
        if category in {"rag", "hybrid", "triage"}:
            required.add(category)
    return required


def _check_qdrant_readiness() -> ReadinessStatus:
    cfg = load_config()
    url = f"{cfg.qdrant_url.rstrip('/')}/collections"
    try:
        with urllib.request.urlopen(url, timeout=max(cfg.qdrant_timeout_s, 2.0)) as response:
            status = getattr(response, "status", None) or response.getcode()
        if int(status) < 400:
            return ReadinessStatus(service="qdrant", ok=True, detail=f"reachable at {cfg.qdrant_url}")
        return ReadinessStatus(service="qdrant", ok=False, detail=f"unexpected HTTP status {status} from {url}")
    except urllib.error.URLError as exc:
        return ReadinessStatus(service="qdrant", ok=False, detail=f"unreachable at {cfg.qdrant_url}: {exc.reason}")
    except Exception as exc:
        return ReadinessStatus(service="qdrant", ok=False, detail=f"unreachable at {cfg.qdrant_url}: {exc}")


def validate_benchmark_readiness(cases: Sequence[Dict[str, Any]]) -> List[ReadinessStatus]:
    statuses: List[ReadinessStatus] = []
    if _categories_requiring_qdrant(cases):
        statuses.append(_check_qdrant_readiness())
    return statuses


def ensure_benchmark_readiness(cases: Sequence[Dict[str, Any]]) -> None:
    statuses = validate_benchmark_readiness(cases)
    failures = [status for status in statuses if not status.ok]
    if not failures:
        return
    details = "; ".join(f"{status.service}: {status.detail}" for status in failures)
    raise RuntimeError(
        "Benchmark readiness check failed. "
        f"{details}. Start the required services before running retrieval-backed benchmarks."
    )


def _get_nested(mapping: Dict[str, Any], path: str) -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _subset_match(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(_subset_match(actual.get(key), value) for key, value in expected.items())
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        actual_norm = [_normalize_text(item) for item in actual]
        return all(_normalize_text(item) in actual_norm for item in expected)
    return actual == expected


def _contains_all(text: Any, expected_parts: Sequence[str]) -> bool:
    haystack = _normalize_text(text)
    return all(_normalize_text(part) in haystack for part in expected_parts)


def _row_count(result: Dict[str, Any]) -> int:
    bundle = result.get("result_bundle") or {}
    rows = bundle.get("rows") or (result.get("sql") or {}).get("rows") or []
    return len(rows) if isinstance(rows, list) else 0


def _has_sql_signal(result: Dict[str, Any]) -> bool:
    sql_text = (
        (result.get("sql") or {}).get("text")
        or result.get("sql_text")
        or (result.get("result_bundle") or {}).get("sql")
        or (result.get("result_bundle") or {}).get("query")
        or ""
    )
    if bool(str(sql_text).strip()):
        return True
    return _row_count(result) > 0


def _rag_count(result: Dict[str, Any]) -> int:
    bundle = result.get("result_bundle") or {}
    rag = bundle.get("rag_snippets") or []
    return len(rag) if isinstance(rag, list) else 0


def _latency_value(result: Dict[str, Any]) -> float:
    raw = result.get("latency")
    try:
        return float(raw)
    except (TypeError, ValueError):
        telemetry = result.get("telemetry") or {}
        try:
            return float(telemetry.get("total_latency_s") or 0.0)
        except (TypeError, ValueError):
            return 0.0


def _did_abstain(result: Dict[str, Any]) -> bool:
    if bool(result.get("abstained")):
        return True
    answer_text = _normalize_text(
        result.get("answer_text")
        or result.get("content")
        or (result.get("result_bundle") or {}).get("summary")
    )
    abstention_markers = [
        "not enough grounded evidence",
        "insufficient evidence",
        "cannot answer this confidently",
        "do not have enough",
        "no grounded evidence",
    ]
    return any(marker in answer_text for marker in abstention_markers)


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 4)
    rank = (len(ordered) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    interpolated = ordered[lower] * (1 - weight) + ordered[upper] * weight
    return round(interpolated, 4)


def _bucket_from_results(results: Sequence[CaseResult], selector) -> Dict[str, AggregateBucket]:
    grouped: Dict[str, list[CaseResult]] = {}
    for result in results:
        key = selector(result)
        grouped.setdefault(key or "unknown", []).append(result)
    summary: Dict[str, AggregateBucket] = {}
    for key, items in grouped.items():
        total = len(items)
        passed = sum(1 for item in items if item.passed)
        failed = total - passed
        summary[key] = AggregateBucket(
            total=total,
            passed=passed,
            failed=failed,
            pass_rate=round((passed / total) * 100, 2) if total else 0.0,
        )
    return dict(sorted(summary.items(), key=lambda pair: pair[0]))


def _build_summary(results: Sequence[CaseResult]) -> BenchmarkSummary:
    all_assertions = [assertion for result in results for assertion in result.assertions]
    assertion_total = len(all_assertions)
    assertion_passed = sum(1 for assertion in all_assertions if assertion.passed)
    assertion_failed = assertion_total - assertion_passed
    assertion_pass_rate = round((assertion_passed / assertion_total) * 100, 2) if assertion_total else 0.0

    latencies = [
        float(result.result.get("latency") or 0.0)
        for result in results
        if not result.error and isinstance(result.result, dict)
    ]
    latency = LatencySummary(
        count=len(latencies),
        avg_s=round(mean(latencies), 4) if latencies else 0.0,
        p50_s=_percentile(latencies, 0.5),
        p95_s=_percentile(latencies, 0.95),
        max_s=round(max(latencies), 4) if latencies else 0.0,
    )

    sql_cases = [result for result in results if result.category == "sql"]
    rag_cases = [result for result in results if result.category == "rag"]
    hybrid_cases = [result for result in results if result.category == "hybrid"]

    return BenchmarkSummary(
        assertion_total=assertion_total,
        assertion_passed=assertion_passed,
        assertion_failed=assertion_failed,
        assertion_pass_rate=assertion_pass_rate,
        category_breakdown=_bucket_from_results(results, lambda result: result.category),
        intent_breakdown=_bucket_from_results(results, lambda result: str(result.result.get("intent") or "unknown")),
        policy_breakdown=_bucket_from_results(results, lambda result: str(result.result.get("policy") or "unknown")),
        latency=latency,
        sql_cases=len(sql_cases),
        sql_cases_passed=sum(1 for result in sql_cases if result.passed),
        rag_cases=len(rag_cases),
        rag_cases_passed=sum(1 for result in rag_cases if result.passed),
        hybrid_cases=len(hybrid_cases),
        hybrid_cases_passed=sum(1 for result in hybrid_cases if result.passed),
    )


@contextmanager
def _model_env(model_config: Optional[ModelConfig]) -> Iterator[None]:
    if model_config is None:
        load_config(refresh=True)
        try:
            yield
        finally:
            load_config(refresh=True)
        return

    overrides = {
        "WTCHTWR_OPENAI_MODEL": model_config.openai_model,
        "WTCHTWR_OPENAI_FALLBACK_MODEL": model_config.openai_fallback_model,
        "WTCHTWR_NL2SQL_MODEL": model_config.nl2sql_model,
        "WTCHTWR_NL2SQL_FALLBACK_MODEL": model_config.nl2sql_fallback_model,
    }
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        load_config(refresh=True)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        load_config(refresh=True)


def evaluate_case(case: Dict[str, Any], *, model_config: Optional[ModelConfig] = None) -> CaseResult:
    case_id = str(case.get("id") or "unnamed-case")
    query = str(case.get("query") or "").strip()
    category = str(case.get("category") or "uncategorized")
    tags = [str(tag) for tag in (case.get("tags") or [])]
    if not query:
        return CaseResult(case_id=case_id, query=query, category=category, tags=tags, passed=False, error="Case missing query.")

    tenant = case.get("tenant")
    user_filters = case.get("user_filters")
    composer_enabled = bool(case.get("composer_enabled", False))
    debug_thinking = bool(case.get("debug_thinking", False))

    try:
        with _model_env(model_config):
            result = run_agent(
                query,
                tenant=tenant,
                user_filters=user_filters,
                history=[],
                composer_enabled=composer_enabled,
                debug_thinking=debug_thinking,
                thread_id=f"benchmark-{case_id}",
            )
    except Exception as exc:
        return CaseResult(case_id=case_id, query=query, category=category, tags=tags, passed=False, error=str(exc))

    assertions: List[AssertionResult] = []
    expected = case.get("expected") or {}

    def add_assertion(name: str, passed: bool, *, expected_value: Any = None, actual_value: Any = None, detail: str | None = None) -> None:
        assertions.append(
            AssertionResult(
                name=name,
                passed=passed,
                expected=expected_value,
                actual=actual_value,
                detail=detail,
            )
        )

    if "intent" in expected:
        actual = result.get("intent")
        add_assertion("intent", actual == expected["intent"], expected_value=expected["intent"], actual_value=actual)

    if "policy" in expected:
        actual = (result.get("result_bundle") or {}).get("policy") or result.get("policy")
        add_assertion("policy", actual == expected["policy"], expected_value=expected["policy"], actual_value=actual)

    if "scope" in expected:
        actual = result.get("scope")
        add_assertion("scope", actual == expected["scope"], expected_value=expected["scope"], actual_value=actual)

    if "filters_subset" in expected:
        actual = result.get("filters") or {}
        passed = _subset_match(actual, expected["filters_subset"])
        add_assertion("filters_subset", passed, expected_value=expected["filters_subset"], actual_value=actual)

    if "sql_contains" in expected:
        sql_text = ((result.get("sql") or {}).get("text") or result.get("sql_text") or (result.get("result_bundle") or {}).get("sql") or "")
        passed = _contains_all(sql_text, expected["sql_contains"])
        add_assertion("sql_contains", passed, expected_value=expected["sql_contains"], actual_value=sql_text)

    if "answer_contains" in expected:
        answer_text = result.get("answer_text") or ""
        passed = _contains_all(answer_text, expected["answer_contains"])
        add_assertion("answer_contains", passed, expected_value=expected["answer_contains"], actual_value=answer_text)

    if "require_sql" in expected:
        actual = _has_sql_signal(result)
        add_assertion("require_sql", actual == bool(expected["require_sql"]), expected_value=bool(expected["require_sql"]), actual_value=actual)

    if "min_rows" in expected:
        actual = _row_count(result)
        add_assertion("min_rows", actual >= int(expected["min_rows"]), expected_value=expected["min_rows"], actual_value=actual)

    if "max_rows" in expected:
        actual = _row_count(result)
        add_assertion("max_rows", actual <= int(expected["max_rows"]), expected_value=expected["max_rows"], actual_value=actual)

    if "min_rag_snippets" in expected:
        actual = _rag_count(result)
        add_assertion("min_rag_snippets", actual >= int(expected["min_rag_snippets"]), expected_value=expected["min_rag_snippets"], actual_value=actual)

    if "field_equals" in expected:
        for field_path, expected_value in (expected["field_equals"] or {}).items():
            actual_value = _get_nested(result, field_path)
            add_assertion(
                f"field_equals:{field_path}",
                actual_value == expected_value,
                expected_value=expected_value,
                actual_value=actual_value,
            )

    if "require_abstain" in expected:
        actual = _did_abstain(result)
        add_assertion(
            "require_abstain",
            actual == bool(expected["require_abstain"]),
            expected_value=bool(expected["require_abstain"]),
            actual_value=actual,
        )

    passed = bool(assertions) and all(assertion.passed for assertion in assertions)
    if not assertions:
        passed = True

    compact_result = {
        "intent": result.get("intent"),
        "scope": result.get("scope"),
        "policy": (result.get("result_bundle") or {}).get("policy") or result.get("policy"),
        "filters": result.get("filters"),
        "sql_text": ((result.get("sql") or {}).get("text") or result.get("sql_text") or (result.get("result_bundle") or {}).get("sql")),
        "answer_text": result.get("answer_text") or result.get("content") or (result.get("result_bundle") or {}).get("summary"),
        "row_count": _row_count(result),
        "rag_count": _rag_count(result),
        "latency": result.get("latency"),
        "abstained": _did_abstain(result),
        "manual_checks": case.get("manual_checks") or [],
        "notes": case.get("notes"),
    }
    return CaseResult(case_id=case_id, query=query, category=category, tags=tags, passed=passed, assertions=assertions, result=compact_result)


def run_benchmarks(
    benchmark_file: Path,
    *,
    case_ids: Optional[Sequence[str]] = None,
    model_config: Optional[ModelConfig] = None,
) -> BenchmarkReport:
    cases = load_benchmarks(benchmark_file)
    if case_ids:
        selected = set(case_ids)
        cases = [case for case in cases if str(case.get("id")) in selected]

    ensure_benchmark_readiness(cases)

    results = [evaluate_case(case, model_config=model_config) for case in cases]
    passed_cases = sum(1 for result in results if result.passed)
    total_cases = len(results)
    failed_cases = total_cases - passed_cases
    pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases else 0.0

    summary = _build_summary(results)

    return BenchmarkReport(
        benchmark_file=str(benchmark_file),
        generated_at=datetime.now(tz=UTC).isoformat(),
        model_label=(model_config.label if model_config else "default"),
        openai_model=(model_config.openai_model if model_config else None),
        openai_fallback_model=(model_config.openai_fallback_model if model_config else None),
        nl2sql_model=(model_config.nl2sql_model if model_config else None),
        nl2sql_fallback_model=(model_config.nl2sql_fallback_model if model_config else None),
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        pass_rate=pass_rate,
        summary=summary,
        results=results,
    )


def report_to_json(report: BenchmarkReport) -> str:
    payload = asdict(report)
    return json.dumps(payload, indent=2)


def report_to_markdown(report: BenchmarkReport) -> str:
    lines = [
        "# wtchtwr Benchmark Report",
        "",
        f"- Benchmark file: `{report.benchmark_file}`",
        f"- Generated at: `{report.generated_at}`",
        f"- Model label: `{report.model_label}`",
        f"- Main model: `{report.openai_model or 'env/default'}`",
        f"- Main fallback: `{report.openai_fallback_model or 'env/default'}`",
        f"- NL2SQL model: `{report.nl2sql_model or 'env/default'}`",
        f"- NL2SQL fallback: `{report.nl2sql_fallback_model or 'env/default'}`",
        f"- Cases: `{report.total_cases}`",
        f"- Passed: `{report.passed_cases}`",
        f"- Failed: `{report.failed_cases}`",
        f"- Pass rate: `{report.pass_rate}%`",
        "",
        "## Summary Metrics",
        "",
        f"- Assertion accuracy: `{report.summary.assertion_pass_rate}%` ({report.summary.assertion_passed}/{report.summary.assertion_total})",
        f"- Average latency: `{report.summary.latency.avg_s}s`",
        f"- P50 latency: `{report.summary.latency.p50_s}s`",
        f"- P95 latency: `{report.summary.latency.p95_s}s`",
        f"- Max latency: `{report.summary.latency.max_s}s`",
        f"- SQL cases passing: `{report.summary.sql_cases_passed}/{report.summary.sql_cases}`",
        f"- RAG cases passing: `{report.summary.rag_cases_passed}/{report.summary.rag_cases}`",
        f"- Hybrid cases passing: `{report.summary.hybrid_cases_passed}/{report.summary.hybrid_cases}`",
        "",
        "### Accuracy By Category",
        "",
    ]
    for name, bucket in report.summary.category_breakdown.items():
        lines.append(f"- `{name}`: `{bucket.pass_rate}%` ({bucket.passed}/{bucket.total})")
    lines.extend(["", "### Accuracy By Policy", ""])
    for name, bucket in report.summary.policy_breakdown.items():
        lines.append(f"- `{name}`: `{bucket.pass_rate}%` ({bucket.passed}/{bucket.total})")
    lines.extend(["", "### Accuracy By Intent", ""])
    for name, bucket in report.summary.intent_breakdown.items():
        lines.append(f"- `{name}`: `{bucket.pass_rate}%` ({bucket.passed}/{bucket.total})")
    lines.append("")
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        lines.append(f"## {result.case_id} [{status}]")
        lines.append("")
        lines.append(f"- Query: `{result.query}`")
        lines.append(f"- Category: `{result.category}`")
        if result.tags:
            lines.append(f"- Tags: `{', '.join(result.tags)}`")
        if result.error:
            lines.append(f"- Error: `{result.error}`")
            lines.append("")
            continue
        outcome = result.result
        lines.append(f"- Intent: `{outcome.get('intent')}`")
        lines.append(f"- Policy: `{outcome.get('policy')}`")
        lines.append(f"- Scope: `{outcome.get('scope')}`")
        lines.append(f"- Row count: `{outcome.get('row_count')}`")
        lines.append(f"- RAG count: `{outcome.get('rag_count')}`")
        lines.append(f"- Latency: `{outcome.get('latency')}`")
        if outcome.get("manual_checks"):
            lines.append("- Manual checks:")
            for item in outcome["manual_checks"]:
                lines.append(f"  - {item}")
        if result.assertions:
            lines.append("- Assertions:")
            for assertion in result.assertions:
                marker = "PASS" if assertion.passed else "FAIL"
                lines.append(f"  - [{marker}] `{assertion.name}`")
                if assertion.expected is not None:
                    lines.append(f"    expected: `{assertion.expected}`")
                if assertion.actual is not None:
                    lines.append(f"    actual: `{assertion.actual}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
