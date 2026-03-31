from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .business_kpis import build_business_kpi_snapshot
from .data_trust import build_data_quality_snapshot, default_paths
from evals.interview_summary import build_interview_summary, load_report


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def _band(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _token_summary(telemetry: Dict[str, Any]) -> Dict[str, Any]:
    usage = telemetry.get("llm_usage") if isinstance(telemetry.get("llm_usage"), dict) else {}
    prompt_tokens = int(usage.get("prompt_tokens") or 0)
    completion_tokens = int(usage.get("completion_tokens") or 0)
    total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens) or 0)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def build_confidence_payload(
    *,
    result: Dict[str, Any],
    bundle: Dict[str, Any],
    state_snapshot: Dict[str, Any],
    telemetry: Dict[str, Any],
) -> Dict[str, Any]:
    state_rag = state_snapshot.get("rag") if isinstance(state_snapshot.get("rag"), dict) else {}
    rag_snippets = bundle.get("rag_snippets") if isinstance(bundle.get("rag_snippets"), list) else []
    response_type = str(result.get("response_type") or "").lower()
    sql_text = (
        (result.get("sql") or {}).get("text")
        or result.get("sql_text")
        or bundle.get("sql")
        or ""
    )
    rows = bundle.get("rows") if isinstance(bundle.get("rows"), list) else []
    rag_error = telemetry.get("rag_error")
    rag_count = len(rag_snippets)
    weak_evidence = bool(state_rag.get("weak_evidence"))
    rag_state_confidence = str(state_rag.get("confidence") or "").lower()
    citations = state_rag.get("citations") if isinstance(state_rag.get("citations"), list) else []
    evidence_count = int(state_rag.get("evidence_count") or rag_count or 0)

    sql_score = 0.15
    sql_reasons: List[str] = []
    if str(sql_text).strip():
        sql_score = 0.62
        sql_reasons.append("Generated SQL for the answer path.")
    if rows:
        sql_score = 0.92 if len(rows) >= 1 else 0.74
        sql_reasons.append(f"Executed SQL returned {len(rows)} row(s).")
    elif str(sql_text).strip():
        sql_reasons.append("SQL exists but the result bundle has no rows.")
    else:
        sql_reasons.append("No SQL evidence was produced for this answer.")

    rag_score = 0.1
    rag_reasons: List[str] = []
    if rag_error:
        rag_reasons.append(f"Retrieval degraded: {rag_error}")
    elif rag_count >= 4 and not weak_evidence:
        rag_score = 0.9
        rag_reasons.append(f"Retrieved {rag_count} grounded review snippets.")
    elif rag_count >= 2:
        rag_score = 0.65
        rag_reasons.append(f"Retrieved {rag_count} review snippets, but evidence is still partial.")
    elif rag_count == 1:
        rag_score = 0.45
        rag_reasons.append("Only one review snippet supported the answer.")
    else:
        rag_reasons.append("No retrieved review evidence was available.")

    if weak_evidence:
        rag_score = min(rag_score, 0.45)
        rag_reasons.append("The retrieval layer marked this as weak evidence.")
    if rag_state_confidence in {"positive", "negative", "neutral", "mixed"} and rag_count:
        rag_reasons.append(f"Retrieval sentiment signal was {rag_state_confidence}.")

    degraded_reasons: List[str] = []
    if rag_error:
        degraded_reasons.append("Qdrant retrieval was unavailable for this answer.")
    if weak_evidence:
        degraded_reasons.append("Evidence density was below the strong-grounding threshold.")

    if response_type == "hybrid":
        overall_score = min(sql_score, rag_score)
    elif response_type == "rag":
        overall_score = rag_score
    elif response_type == "sql":
        overall_score = sql_score
    elif response_type == "expansion":
        overall_score = 0.55 if not telemetry.get("expansion_source_count") else 0.75
    else:
        overall_score = 0.5 if (rows or rag_snippets) else 0.35

    if degraded_reasons:
        overall_score = max(0.2, overall_score - 0.15)

    citation_coverage = 0.0
    if response_type == "sql":
        citation_coverage = 1.0 if rows else (0.4 if str(sql_text).strip() else 0.0)
    elif response_type == "rag":
        citation_coverage = min(evidence_count / 4.0, 1.0) if citations or rag_count else 0.0
    elif response_type == "hybrid":
        sql_grounding = 1.0 if rows else (0.5 if str(sql_text).strip() else 0.0)
        rag_grounding = min(evidence_count / 4.0, 1.0) if citations or rag_count else 0.0
        citation_coverage = round((sql_grounding + rag_grounding) / 2.0, 2)
    elif response_type == "expansion":
        source_count = int(telemetry.get("expansion_source_count") or 0)
        citation_coverage = min(source_count / 4.0, 1.0)

    abstain_recommended = False
    if response_type in {"rag", "hybrid"} and (rag_error or (rag_count == 0 and weak_evidence)):
        abstain_recommended = True
    if response_type == "sql" and not rows and not str(sql_text).strip():
        abstain_recommended = True
    if overall_score <= 0.35 and not rows and rag_count <= 1:
        abstain_recommended = True

    overall_score = _clamp_score(overall_score)
    sql_score = _clamp_score(sql_score)
    rag_score = _clamp_score(rag_score)
    citation_coverage = _clamp_score(citation_coverage)

    return {
        "overall": {
            "band": _band(overall_score),
            "score": overall_score,
            "label": "Answer confidence",
            "reasons": degraded_reasons + (
                [f"Combined structured and unstructured evidence for a {response_type} answer."]
                if response_type == "hybrid"
                else ["Confidence derived from the active answer path."]
            ),
        },
        "sql": {
            "band": _band(sql_score),
            "score": sql_score,
            "label": "SQL confidence",
            "reasons": sql_reasons,
        },
        "rag": {
            "band": _band(rag_score),
            "score": rag_score,
            "label": "Retrieval confidence",
            "reasons": rag_reasons,
        },
        "degraded": bool(degraded_reasons),
        "degraded_reasons": degraded_reasons,
        "weak_evidence": weak_evidence,
        "citation_coverage": {
            "band": _band(citation_coverage),
            "score": citation_coverage,
            "label": "Grounding coverage",
            "reasons": [
                "Measures how much of the answer is backed by SQL rows or retrieved evidence.",
            ],
        },
        "evidence_count": evidence_count,
        "abstain_recommended": abstain_recommended,
    }


def build_trace_payload(
    *,
    result: Dict[str, Any],
    bundle: Dict[str, Any],
    state_snapshot: Dict[str, Any],
    telemetry: Dict[str, Any],
    confidence: Dict[str, Any],
) -> Dict[str, Any]:
    filters = state_snapshot.get("filters") if isinstance(state_snapshot.get("filters"), dict) else {}
    rag_state = state_snapshot.get("rag") if isinstance(state_snapshot.get("rag"), dict) else {}
    sql_state = state_snapshot.get("sql") if isinstance(state_snapshot.get("sql"), dict) else {}
    rag_snippets = bundle.get("rag_snippets") if isinstance(bundle.get("rag_snippets"), list) else []
    rows = bundle.get("rows") if isinstance(bundle.get("rows"), list) else []
    sql_text = (
        (result.get("sql") or {}).get("text")
        or result.get("sql_text")
        or bundle.get("sql")
        or sql_state.get("text")
        or ""
    )
    return {
        "intent": result.get("intent") or state_snapshot.get("intent"),
        "scope": result.get("scope") or state_snapshot.get("scope"),
        "policy": bundle.get("policy") or result.get("policy") or telemetry.get("policy"),
        "filters": filters,
        "sql": {
            "present": bool(str(sql_text).strip()),
            "row_count": len(rows),
            "query_preview": str(sql_text).strip()[:800] or None,
            "table": bundle.get("sql_table") or sql_state.get("table"),
        },
        "retrieval": {
            "hit_count": len(rag_snippets),
            "weak_evidence": bool(rag_state.get("weak_evidence")),
            "confidence": rag_state.get("confidence"),
            "summary": rag_state.get("summary"),
            "error": telemetry.get("rag_error"),
            "raw_hit_count": len(rag_state.get("retrieved_hits") or []) if isinstance(rag_state.get("retrieved_hits"), list) else None,
            "reranker": telemetry.get("rag_reranker"),
            "reranked_count": telemetry.get("rag_reranked_count"),
        },
        "performance": {
            "latency_ms": telemetry.get("latency_ms"),
            "total_latency_s": telemetry.get("total_latency_s"),
            "compose_latency_s": telemetry.get("compose_latency_s"),
            "hybrid_sql_latency_s": telemetry.get("hybrid_sql_latency_s"),
            "hybrid_rag_latency_s": telemetry.get("hybrid_rag_latency_s"),
            "routing_latency_s": telemetry.get("intent_latency_s"),
            "sql_latency_s": telemetry.get("sql_total_time_s"),
            "retrieval_latency_s": telemetry.get("rag_total_time_s"),
            "tokens": _token_summary(telemetry),
        },
        "degraded": confidence.get("degraded", False),
        "degraded_reasons": confidence.get("degraded_reasons") or [],
        "abstain_recommended": confidence.get("abstain_recommended", False),
    }


def _safe_load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_data_quality_payload(repo_root: Path) -> Dict[str, Any]:
    report_path = repo_root / "docs" / "reports" / "data-quality-latest.json"
    payload = _safe_load_json(report_path)
    if payload:
        return payload
    try:
        return build_data_quality_snapshot(default_paths(repo_root))
    except Exception as exc:
        return {"status": "unknown", "issues": [f"Unable to load data quality snapshot: {exc}"]}


def _benchmark_history(reports_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for path in sorted(reports_dir.glob("benchmark-report-*.json")):
        try:
            report = load_report(path)
        except Exception:
            continue
        pack_name = Path(report.benchmark_file).stem
        summary = build_interview_summary(report)
        grouped.setdefault(pack_name, []).append(
            {
                "generated_at": report.generated_at,
                "benchmark_report": path.name,
                "overall_pass_rate": summary["pipeline_metrics"]["overall_pass_rate"],
                "assertion_pass_rate": summary["headline_metrics"]["assertion_pass_rate"],
                "sql_pass_rate": summary["pipeline_metrics"]["sql_pass_rate"],
                "rag_pass_rate": summary["pipeline_metrics"]["rag_pass_rate"],
                "hybrid_pass_rate": summary["pipeline_metrics"]["hybrid_pass_rate"],
                "p50_latency_s": summary["performance_metrics"]["p50_latency_s"],
                "p95_latency_s": summary["performance_metrics"]["p95_latency_s"],
            }
        )
    return {pack: history[-12:] for pack, history in grouped.items()}


def _latest_benchmark_reports(reports_dir: Path) -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, tuple[str, Path]] = {}
    for path in reports_dir.glob("benchmark-report-*.json"):
        try:
            report = load_report(path)
        except Exception:
            continue
        pack_name = Path(report.benchmark_file).stem
        current = latest.get(pack_name)
        if current is None or report.generated_at > current[0]:
            latest[pack_name] = (report.generated_at, path)

    payloads: Dict[str, Dict[str, Any]] = {}
    for pack_name, (_, path) in latest.items():
        report = load_report(path)
        summary = build_interview_summary(report)
        case_details: List[Dict[str, Any]] = []
        for result in report.results:
            compact = result.result or {}
            case_details.append(
                {
                    "case_id": result.case_id,
                    "query": result.query,
                    "category": result.category,
                    "passed": result.passed,
                    "tags": result.tags,
                    "intent": compact.get("intent"),
                    "scope": compact.get("scope"),
                    "policy": compact.get("policy"),
                    "answer_text": compact.get("answer_text"),
                    "sql_text": compact.get("sql_text"),
                    "row_count": compact.get("row_count"),
                    "rag_count": compact.get("rag_count"),
                    "latency": compact.get("latency"),
                    "abstained": compact.get("abstained"),
                    "manual_checks": compact.get("manual_checks") or [],
                    "notes": compact.get("notes"),
                    "error": result.error,
                    "assertions": [
                        {
                            "name": assertion.name,
                            "passed": assertion.passed,
                            "expected": assertion.expected,
                            "actual": assertion.actual,
                            "detail": assertion.detail,
                        }
                        for assertion in result.assertions
                    ],
                }
            )
        payloads[pack_name] = {
            "pack": pack_name,
            "benchmark_report": path.name,
            "benchmark_file": report.benchmark_file,
            "generated_at": report.generated_at,
            "model_label": summary.get("model_label"),
            "headline_metrics": summary["headline_metrics"],
            "performance_metrics": summary["performance_metrics"],
            "pipeline_metrics": summary["pipeline_metrics"],
            "strongest_categories": summary["strongest_categories"],
            "weakest_categories": summary["weakest_categories"],
            "failed_case_ids": summary["failed_case_ids"],
            "failed_case_count": summary["failed_case_count"],
            "slowest_cases": summary["slowest_cases"],
            "policy_breakdown": summary["policy_breakdown"],
            "intent_breakdown": summary["intent_breakdown"],
            "delta_vs_previous": summary["delta_vs_previous"],
            "interview_talking_points": summary["interview_talking_points"],
            "case_details": case_details,
        }
    return payloads


def load_ai_metrics_payload(reports_dir: Path, health_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    repo_root = reports_dir.parents[1]
    interview_latest = _safe_load_json(reports_dir / "interview-metrics-latest.json")
    interview_default = _safe_load_json(reports_dir / "interview-metrics.json")
    latest_packs = _latest_benchmark_reports(reports_dir)
    benchmark_history = _benchmark_history(reports_dir)
    business_kpis: Dict[str, Any]
    try:
        business_kpis = build_business_kpi_snapshot(repo_root)
    except Exception as exc:
        business_kpis = {"error": str(exc)}
    data_quality = _load_data_quality_payload(repo_root)
    return {
        "service": "wtchtwr-ai-observability",
        "generated_at": health_snapshot.get("checked_at"),
        "health": health_snapshot,
        "latest_interview_metrics": interview_latest or interview_default,
        "packs": latest_packs,
        "pack_history": benchmark_history,
        "data_quality": data_quality,
        "business_kpis": business_kpis,
    }
