"""Challenge memos for the seven default theses.

Theses inherit the parent need score. They are not a second index.
Every memo must carry a bear case, counterarguments, and kill criteria.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from cf_atlas.paths import external_dir, processed_dir, repo_root

REQUIRED_TEXT = (
    "headline",
    "fact",
    "analysis",
    "interpretation",
    "bull_case",
    "bear_case",
    "verdict",
)
REQUIRED_LISTS = ("counterarguments", "remaining_diligence")

STANCE_LABELS = {
    "pursue_diligence": "Pursue diligence",
    "watch_adjacent": "Watch adjacent",
    "watch_incumbents": "Watch incumbents",
    "services_not_drug": "Services, not a drug",
}

DISCLAIMER = (
    "Not medical advice, not a recommendation to buy or sell any security, "
    "and not a claim that any opportunity should be funded. Scores are an "
    "exploratory index. Theses inherit the parent need score; they are not "
    "a second ranking."
)


def challenges_path() -> Path:
    return external_dir() / "thesis_challenges.json"


def load_challenges() -> dict:
    payload = json.loads(challenges_path().read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "theses" not in payload:
        raise ValueError("thesis_challenges.json must be an object with a theses array.")
    return payload


def _nonempty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(_nonempty(item) for item in value)
    return True


def validate_challenges(payload: dict | None = None) -> dict:
    payload = payload or load_challenges()
    theses = payload["theses"]
    ids = [row["thesis_id"] for row in theses]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate thesis_id in thesis_challenges.json")
    if not (5 <= len(theses) <= 7):
        raise ValueError(f"Expected 5–7 theses, found {len(theses)}")
    for row in theses:
        tid = row.get("thesis_id", "?")
        for key in REQUIRED_TEXT:
            if not _nonempty(row.get(key)):
                raise ValueError(f"{tid} is missing {key}")
        for key in REQUIRED_LISTS:
            if not _nonempty(row.get(key)):
                raise ValueError(f"{tid} is missing {key}")
        if len(row["bear_case"].strip()) < 80:
            raise ValueError(f"{tid} bear_case is too short to be a real challenge")
        if len(row["counterarguments"]) < 2:
            raise ValueError(f"{tid} needs at least two counterarguments")
        bull = row["bull_case"].lower()
        bear = row["bear_case"].lower()
        if bull == bear:
            raise ValueError(f"{tid} bull and bear cases are identical")
    held = payload.get("held_out") or []
    held_ids = {row["need_id"] for row in held}
    if held_ids != {"N2", "N7"}:
        raise ValueError("held_out must cover N2 and N7 and nothing else")
    for row in held:
        if not _nonempty(row.get("why_held_out")) or not _nonempty(row.get("verdict")):
            raise ValueError(f"{row.get('need_id')} held-out note is incomplete")
        if not _nonempty(row.get("counterarguments")):
            raise ValueError(f"{row.get('need_id')} held-out note needs counterarguments")
    return payload


def merge_memos(theses: pd.DataFrame, payload: dict | None = None) -> list[dict]:
    payload = validate_challenges(payload)
    by_id = {row["thesis_id"]: row for row in payload["theses"]}
    thesis_ids = set(theses["thesis_id"])
    missing = thesis_ids - set(by_id)
    extra = set(by_id) - thesis_ids
    if missing or extra:
        raise ValueError(f"Thesis challenge mismatch. missing={sorted(missing)} extra={sorted(extra)}")
    merged: list[dict] = []
    for record in json.loads(theses.to_json(orient="records")):
        challenge = by_id[record["thesis_id"]]
        if not _nonempty(record.get("kill_criteria")):
            raise ValueError(f"{record['thesis_id']} is missing kill_criteria")
        if not _nonempty(record.get("what_would_have_to_be_true")):
            raise ValueError(f"{record['thesis_id']} is missing what_would_have_to_be_true")
        merged.append({**record, **challenge})
    return merged


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _memo_markdown(memo: dict) -> str:
    stance = STANCE_LABELS.get(memo["formation_stance"], memo["formation_stance"])
    score = int(memo.get("parent_need_score") or memo.get("display_default") or 0)
    evidence = memo.get("evidence_confidence") or "Moderate"
    return f"""# {memo["thesis_id"]} — {memo["title"]}

**{stance}** · {memo["need_id"]} · Opportunity Score: {score}/100 · Evidence: {evidence}

{DISCLAIMER}

## The claim (HYPOTHESIS)

{memo["headline"]}

{memo["one_liner"]}

## FACT

{memo["fact"]}

## ANALYSIS

{memo["analysis"]}

## INTERPRETATION

{memo["interpretation"]}

## Bull case

{memo["bull_case"]}

## Bear case

{memo["bear_case"]}

## Counterarguments

{_bullets(memo["counterarguments"])}

## What would have to be true

{memo["what_would_have_to_be_true"]}

## Kill criteria

{memo["kill_criteria"]}

## Remaining diligence

{_bullets(memo["remaining_diligence"])}

## Verdict

{memo["verdict"]}
"""


def _held_out_markdown(row: dict) -> str:
    return (
        f"### {row['need_id']} — {row['title']}\n\n"
        f"Default score {int(row['score_default'])}/100.\n\n"
        f"{row['why_held_out']}\n\n"
        f"{_bullets(row['counterarguments'])}\n\n"
        f"**{row['verdict']}**\n"
    )


def _index_markdown(memos: list[dict], held_out: list[dict]) -> str:
    rows = []
    for memo in memos:
        stance = STANCE_LABELS.get(memo["formation_stance"], memo["formation_stance"])
        score = int(memo.get("parent_need_score") or 0)
        rows.append(
            f"| [{memo['thesis_id']}]({memo['thesis_id']}.md) | {stance} | {memo['need_id']} | "
            f"{score} | {memo['title']} |"
        )
    held = "\n".join(_held_out_markdown(row) for row in held_out)
    return f"""# Challenge memos

Seven white-space memos. Each one has a bull case, a bear case, counterarguments, remaining diligence, and kill criteria. No thesis is only a bull case.

Theses inherit the parent need score. They are not a second opportunity index.

{DISCLAIMER}

| ID | Stance | Need | Score | Thesis |
|---|---|---|---|---|
{chr(10).join(rows)}

## Scored, not default company-formation cards

N2 and N7 stay in the investigation set. They do not get default newco cards.

{held}

Regenerate with `python -m cf_atlas theses` after editing `data/external/thesis_challenges.json` or `opportunity_theses.csv`.
"""


def write_markdown(memos: list[dict], held_out: list[dict], destination: Path | None = None) -> Path:
    out_dir = destination or (repo_root() / "docs" / "theses")
    out_dir.mkdir(parents=True, exist_ok=True)
    for memo in memos:
        (out_dir / f"{memo['thesis_id']}.md").write_text(_memo_markdown(memo), encoding="utf-8")
    (out_dir / "README.md").write_text(_index_markdown(memos, held_out), encoding="utf-8")
    return out_dir


def write_processed(memos: list[dict], held_out: list[dict], destination: Path | None = None) -> Path:
    out = destination or (processed_dir() / "scoring" / "thesis_memos.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"theses": memos, "held_out": held_out}, indent=2),
        encoding="utf-8",
    )
    return out


def run_theses(theses: pd.DataFrame | None = None) -> dict[str, str | int]:
    payload = validate_challenges()
    if theses is None:
        path = processed_dir() / "scoring" / "theses.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run `python -m cf_atlas score` first.")
        theses = pd.read_csv(path)
    memos = merge_memos(theses, payload)
    docs_dir = write_markdown(memos, payload["held_out"])
    processed = write_processed(memos, payload["held_out"])
    return {
        "docs_dir": str(docs_dir),
        "processed": str(processed),
        "theses": len(memos),
        "held_out": len(payload["held_out"]),
    }
