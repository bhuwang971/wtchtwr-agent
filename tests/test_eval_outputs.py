from pathlib import Path

from scripts.run_benchmarks import _pack_slug


def test_pack_slug_for_local_and_holdout_files() -> None:
    assert _pack_slug(Path("evals/benchmarks.local.json")) == "local"
    assert _pack_slug(Path("evals/benchmarks.holdout.json")) == "holdout"
    assert _pack_slug(Path("evals/custom-pack.json")) == "custom-pack"
