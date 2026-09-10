"""Export dated processed tables into the Next.js app snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from cf_atlas.paths import external_dir, processed_dir, repo_root
from cf_atlas.theses import load_challenges, merge_memos, run_theses, validate_challenges


def _records(path: Path) -> list[dict]:
    frame = pd.read_csv(path)
    return json.loads(frame.to_json(orient="records"))


def build_snapshot() -> dict:
    processed = processed_dir()
    landscape = processed / "landscape"
    classification = processed / "classification"
    scoring = processed / "scoring"
    required = [
        landscape / "landscape_claims.csv",
        landscape / "solved_unsolved.csv",
        landscape / "trials_by_year.csv",
        classification / "classification_summary.csv",
        classification / "competitive_map.csv",
        classification / "map_assets.csv",
        classification / "need_pipeline_coverage.csv",
        scoring / "need_scores.csv",
        scoring / "theses.csv",
        scoring / "rank_stability.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing processed tables. Run landscape, classify, and score first: "
            + "; ".join(missing)
        )
    challenges = validate_challenges(load_challenges())
    theses = merge_memos(pd.read_csv(scoring / "theses.csv"), challenges)
    return {
        "meta": {
            "registry_year": 2024,
            "registry_source": "CFF Patient Registry 2024 Annual Data Report",
            "trials_retrieved_at": "2026-09-09T22:49:42Z",
            "trials_source": "ClinicalTrials.gov API v2, interventional, query.cond=cystic fibrosis",
            "disclaimer": (
                "Not medical advice, not a recommendation to buy or sell any security, "
                "and not a claim that any opportunity should be funded."
            ),
        },
        "claims": _records(landscape / "landscape_claims.csv"),
        "solved_unsolved": _records(landscape / "solved_unsolved.csv"),
        "trials_by_year": _records(landscape / "trials_by_year.csv"),
        "classification_summary": _records(classification / "classification_summary.csv"),
        "competitive_map": _records(classification / "competitive_map.csv"),
        "map_assets": _records(classification / "map_assets.csv"),
        "need_coverage": _records(classification / "need_pipeline_coverage.csv"),
        "need_scores": _records(scoring / "need_scores.csv"),
        "theses": theses,
        "held_out": challenges["held_out"],
        "rank_stability": _records(scoring / "rank_stability.csv"),
        "weights": _records(external_dir() / "scoring_weights.csv"),
        "component_scores": _records(external_dir() / "component_scores.csv"),
    }


def write_snapshot(destination: Path | None = None) -> Path:
    run_theses()
    out = destination or (repo_root() / "app" / "src" / "data" / "snapshot.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build_snapshot()
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def run_export_app() -> dict[str, str | int]:
    path = write_snapshot()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "snapshot": str(path),
        "needs": len(payload["need_scores"]),
        "theses": len(payload["theses"]),
        "held_out": len(payload["held_out"]),
        "map_assets": len(payload["map_assets"]),
        "claims": len(payload["claims"]),
    }
