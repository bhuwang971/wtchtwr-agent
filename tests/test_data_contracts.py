from pathlib import Path

from backend.data_trust import build_data_quality_snapshot, default_paths, validate_data_contracts


def test_data_contracts_have_no_missing_columns() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = validate_data_contracts(default_paths(repo_root))
    assert report["ok"] is True
    assert all(item["ok"] for item in report["checks"])


def test_data_quality_snapshot_has_expected_sections() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    snapshot = build_data_quality_snapshot(default_paths(repo_root))
    assert "summary" in snapshot
    assert "contracts" in snapshot
    assert "checks" in snapshot
    assert "issues" in snapshot
