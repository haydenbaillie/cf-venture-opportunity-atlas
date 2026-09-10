"""ClinicalTrials.gov Data API v2 ingest."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import httpx
import pandas as pd

from cf_atlas.paths import processed_dir, raw_dir
from cf_atlas.trials import flatten_collaborators, flatten_interventions, flatten_trial

API_BASE = "https://clinicaltrials.gov/api/v2/studies"
SOURCE_ID = "clinicaltrials_gov_api_v2"
DEFAULT_USER_AGENT = None
DEFAULT_QUERY = {
    "query.cond": "cystic fibrosis",
    "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fetch_studies(
    *,
    query: dict[str, str] | None = None,
    page_size: int = 100,
    timeout: float = 90.0,
    user_agent: str | None = DEFAULT_USER_AGENT,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Page through the studies endpoint and return records plus a manifest."""
    params: dict[str, Any] = {
        **(query or DEFAULT_QUERY),
        "pageSize": page_size,
        "countTotal": "true",
        "format": "json",
    }
    retrieved_at = utc_now_iso()
    studies: list[dict[str, Any]] = []
    page = 0
    next_token: str | None = None
    total_count: int | None = None

    headers = {"Accept": "application/json"}
    if user_agent:
        headers["User-Agent"] = user_agent
    with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
        while True:
            page += 1
            call_params = dict(params)
            if next_token:
                call_params["pageToken"] = next_token
                call_params.pop("countTotal", None)
            response = client.get(API_BASE, params=call_params)
            response.raise_for_status()
            payload = response.json()
            if total_count is None:
                total_count = payload.get("totalCount")
            batch = payload.get("studies") or []
            studies.extend(batch)
            next_token = payload.get("nextPageToken")
            if not next_token:
                break
            time.sleep(0.2)

    manifest = {
        "source_id": SOURCE_ID,
        "endpoint": API_BASE,
        "query": query or DEFAULT_QUERY,
        "page_size": page_size,
        "pages_fetched": page,
        "total_count_reported": total_count,
        "records_saved": len(studies),
        "retrieved_at": retrieved_at,
        "notes": (
            "Sponsor-reported registry data. Interventional studies tagged to "
            "cystic fibrosis; condition tagging can be noisy. Does not include "
            "most preclinical programs."
        ),
    }
    return studies, manifest


def write_raw(studies: list[dict[str, Any]], manifest: dict[str, Any]) -> Path:
    destination = raw_dir() / "clinicaltrials"
    destination.mkdir(parents=True, exist_ok=True)
    jsonl_path = destination / "studies.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for study in studies:
            handle.write(json.dumps(study, ensure_ascii=False) + "\n")
    manifest_path = destination / "manifest.json"
    manifest = {**manifest, "output_path": str(jsonl_path.as_posix())}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return jsonl_path


def read_raw_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def process_studies(
    studies: list[dict[str, Any]] | Iterator[dict[str, Any]],
    retrieved_at: str,
    source_id: str = SOURCE_ID,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    trial_rows: list[dict[str, Any]] = []
    intervention_rows: list[dict[str, Any]] = []
    collaborator_rows: list[dict[str, Any]] = []
    for study in studies:
        trial_rows.append(flatten_trial(study, retrieved_at=retrieved_at, source_id=source_id))
        intervention_rows.extend(flatten_interventions(study))
        collaborator_rows.extend(flatten_collaborators(study))
    trials = pd.DataFrame(trial_rows)
    interventions = pd.DataFrame(intervention_rows)
    collaborators = pd.DataFrame(collaborator_rows)
    if not trials.empty:
        trials = trials.sort_values("nct_id").reset_index(drop=True)
        if "enrollment_count" in trials.columns:
            trials["enrollment_count"] = pd.to_numeric(
                trials["enrollment_count"], errors="coerce"
            ).astype("Int64")
        for flag in ("healthy_volunteers", "has_results", "is_fda_regulated_drug"):
            if flag in trials.columns:
                trials[flag] = pd.to_numeric(trials[flag], errors="coerce").astype("Int64")
    return trials, interventions, collaborators


def write_processed(
    trials: pd.DataFrame,
    interventions: pd.DataFrame,
    collaborators: pd.DataFrame,
) -> Path:
    destination = processed_dir()
    destination.mkdir(parents=True, exist_ok=True)
    trials.to_csv(destination / "trials.csv", index=False)
    interventions.to_csv(destination / "trial_interventions.csv", index=False)
    collaborators.to_csv(destination / "trial_collaborators.csv", index=False)
    return destination


def ingest_trials(*, page_size: int = 100) -> dict[str, Any]:
    studies, manifest = fetch_studies(page_size=page_size)
    write_raw(studies, manifest)
    trials, interventions, collaborators = process_studies(
        studies,
        retrieved_at=manifest["retrieved_at"],
    )
    write_processed(trials, interventions, collaborators)
    return {
        **manifest,
        "trial_rows": int(len(trials)),
        "intervention_rows": int(len(interventions)),
        "collaborator_rows": int(len(collaborators)),
    }
