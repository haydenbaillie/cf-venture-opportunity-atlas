"""Phase 4 classification: auto-suggest, review overlay, competitive map.

Auto-suggested labels are written for every trial. Rankings and the competitive
map may use only rows with review_status=reviewed, disease_area=cf, and
map_eligible=1. Unreviewed rows never enter those outputs.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

from cf_atlas.landscape import ACTIVE_STATUSES, connect, flag_ncfb
from cf_atlas.paths import external_dir, processed_dir, repo_root

SOURCE_ID = "clinicaltrials_gov_api_v2"

NEED_BY_STRATEGY: dict[str, str] = {
    "gene_therapy": "N1",
    "mrna": "N1",
    "gene_editing": "N1",
    "aso_oligonucleotide": "N1",
    "genetic_therapy": "N1",
    "nonsense_readthrough": "N1",
    "anion_bypass": "N1",
    "cftr_modulator": "N2",
    "mucociliary_clearance": "N3",
    "anti_inflammatory": "N3",
    "antimicrobial": "N4",
    "phage": "N4",
    "antifungal": "N4",
    "metabolic_cfrd": "N5",
    "gi_nutrition": "N6",
    "care_delivery": "N8",
    "diagnostic": "",
    "other": "",
}

STAGE_ORDER = (
    "preclinical",
    "phase_1",
    "phase_2",
    "phase_3",
    "approved",
    "standard_of_care",
    "not_applicable",
)

# First matching rule wins. Patterns are applied to title + summary + conditions
# + intervention names.
STRATEGY_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("phage", re.compile(r"\b(phage|bacteriophage|bx004|ap-pa02|achromophage)\b", re.I), "phage"),
    (
        "mrna",
        re.compile(
            r"\b(cftr mrna|vx-522|arct-032|rct2100|bmd003|lunar-cf|mrna therap)\b",
            re.I,
        ),
        "mrna",
    ),
    (
        "gene_therapy",
        re.compile(
            r"\b(4d-710|kb407|sp-101|bi 3720931|gene therap|aav\b|viral-vector cftr)\b",
            re.I,
        ),
        "gene_therapy",
    ),
    (
        "aso",
        re.compile(r"\b(spl84|antisense|oligonucleotide|splicing oligo|eluforsen|qr-010)\b", re.I),
        "aso_oligonucleotide",
    ),
    (
        "nonsense",
        re.compile(r"\b(ataluren|elx-02|readthrough|nonsense mutation)\b", re.I),
        "nonsense_readthrough",
    ),
    (
        "anion_bypass",
        re.compile(r"\b(abci|amphotericin b cystetic|ionophore|anion transport)\b", re.I),
        "anion_bypass",
    ),
    (
        "modulator",
        re.compile(
            r"\b(elexacaftor|tezacaftor|ivacaftor|vanzacaftor|deutivacaftor|"
            r"trikafta|alyftrek|orkambi|kalydeco|symdeko|sion-\d+|vx-581|"
            r"vx-272|vx-828|vx-121|cftr modulator|modulator therap)\b",
            re.I,
        ),
        "cftr_modulator",
    ),
    (
        "cfrd",
        re.compile(
            r"\b(cfrd|cystic fibrosis-related diabetes|cystic fibrosis related diabetes|"
            r"bionic pancreas|empagliflozin|dulaglutide|metformin|dorzagliatin|"
            r"sglt2|glp-1|verapamil|dysglycemia|glucose intolerance)\b",
            re.I,
        ),
        "metabolic_cfrd",
    ),
    (
        "gi",
        re.compile(
            r"\b(ang003|nhs7108|pancrelipase|lipase|pert\b|maralixibat|tenapanor|"
            r"linaclotide|constipation|relizorb|adrulipase|exocrine pancre)\b",
            re.I,
        ),
        "gi_nutrition",
    ),
    (
        "gallium_ntm",
        re.compile(r"\b(gallium|nontuberculous|nontuberculosis mycobacter|ntm\b|mycoba)\b", re.I),
        "antimicrobial",
    ),
    (
        "anti_inflammatory",
        re.compile(
            r"\b(anakinra|losartan|ibuprofen|acebilustat|brensocatib|verducatib|"
            r"lau-7b|anti-inflamm|dpp1)\b",
            re.I,
        ),
        "anti_inflammatory",
    ),
    (
        "antifungal",
        re.compile(r"\b(opelconazole|aspergillus|antifungal|azole)\b", re.I),
        "antifungal",
    ),
    (
        "antimicrobial",
        re.compile(
            r"\b(tobramycin|aztreonam|amikacin|azithromycin|antibiotic|antimicrobial)\b",
            re.I,
        ),
        "antimicrobial",
    ),
    (
        "mucociliary",
        re.compile(
            r"\b(hypertonic saline|dornase|pulmozyme|mannitol|bronchitol|"
            r"airway clearance|hfcwo|oscillat|pep device|o-pep|mucolytic)\b",
            re.I,
        ),
        "mucociliary_clearance",
    ),
    (
        "diagnostic",
        re.compile(
            r"\b(sweat test|sweat chloride|xenon|129xe|mri|imaging biomarker|"
            r"diagnostic|n-of-1|theratyping)\b",
            re.I,
        ),
        "diagnostic",
    ),
    (
        "care_delivery",
        re.compile(
            r"\b(yoga|exercise|telehealth|tele-rehab|mobile health|mhealth|"
            r"cognitive behavioral|wellness|education resource|self-help|"
            r"air purifier|mediterranean diet|physical activity|digital)\b",
            re.I,
        ),
        "care_delivery",
    ),
]


def crowding_band(n: int) -> str:
    if n >= 5:
        return "high"
    if n >= 2:
        return "moderate"
    if n == 1:
        return "low"
    return "none"


def normalize_stage(phase: str | None, development_stage: str | None = None) -> str:
    raw = (development_stage or phase or "").strip().lower().replace(" ", "_")
    aliases = {
        "phase_one": "phase_1",
        "phase1": "phase_1",
        "early_phase1": "phase_1",
        "phase_two": "phase_2",
        "phase2": "phase_2",
        "phase_three": "phase_3",
        "phase3": "phase_3",
        "phase_four": "approved",
        "phase4": "approved",
        "to_patients": "approved",
        "standard_of_care": "standard_of_care",
        "approved": "approved",
        "preclinical": "preclinical",
        "na": "not_applicable",
        "": "not_applicable",
    }
    if raw in aliases:
        return aliases[raw]
    if "phase1;phase2" in raw or "phase_1;phase_2" in raw:
        return "phase_1"
    if "phase2;phase3" in raw or "phase_2;phase_3" in raw:
        return "phase_2"
    if raw.startswith("phase_1") or raw == "phase1":
        return "phase_1"
    if "phase_3" in raw or raw == "phase3":
        return "phase_3"
    if "phase_2" in raw or raw == "phase2":
        return "phase_2"
    if "phase_4" in raw or raw == "phase4":
        return "approved"
    if "preclinical" in raw:
        return "preclinical"
    if "approv" in raw:
        return "approved"
    return "not_applicable"


def suggest_strategy(blob: str) -> tuple[str, str]:
    text = blob or ""
    for rule_id, pattern, strategy in STRATEGY_RULES:
        if pattern.search(text):
            return strategy, rule_id
    return "other", "no_keyword_match"


def suggest_role(strategy: str, phase: str | None, intervention_types: str) -> str:
    if strategy == "diagnostic":
        return "diagnostic"
    if strategy == "care_delivery":
        return "supportive"
    types = {part.strip().upper() for part in (intervention_types or "").split("|") if part.strip()}
    druglike = types & {"DRUG", "BIOLOGICAL", "COMBINATION_PRODUCT"}
    if not druglike and types and types <= {"BEHAVIORAL", "DEVICE", "DIAGNOSTIC_TEST", "OTHER", "PROCEDURE", "DIETARY_SUPPLEMENT"}:
        if strategy in {"mucociliary_clearance", "care_delivery"}:
            return "supportive"
        if "DIAGNOSTIC_TEST" in types or "DEVICE" in types:
            return "diagnostic"
        return "supportive"
    if (phase or "").upper() == "PHASE4" and strategy == "cftr_modulator":
        return "label_expansion"
    if strategy == "other":
        return "supportive"
    return "therapeutic"


def suggest_trial_row(blob: str, phase: str | None, intervention_types: str, ncfb_reason: str | None) -> dict[str, str]:
    strategy, rule_id = suggest_strategy(blob)
    flagged = bool(ncfb_reason) and not (isinstance(ncfb_reason, float) and pd.isna(ncfb_reason))
    disease_area = "ncfb" if flagged else "cf"
    if disease_area == "ncfb":
        need_ids = ""
        role = "not_cf_primary"
    else:
        need_ids = NEED_BY_STRATEGY.get(strategy, "")
        role = suggest_role(strategy, phase, intervention_types)
    return {
        "strategy": strategy,
        "strategy_rule_id": rule_id,
        "disease_area": disease_area,
        "need_ids": need_ids,
        "role": role,
        "map_eligible": 0,
        "whitespace_relevant": 0,
        "crowding_unit": 0,
        "review_status": "auto_suggested",
        "review_source": "rules",
    }


def _blob_from_trial(row: pd.Series) -> str:
    parts = [
        row.get("brief_title"),
        row.get("official_title"),
        row.get("brief_summary"),
        row.get("conditions"),
        row.get("intervention_names"),
        row.get("intervention_types"),
    ]
    return " ".join(str(p) for p in parts if p and not (isinstance(p, float) and pd.isna(p)))


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, dtype=str).fillna("")


def trial_frame(conn: sqlite3.Connection) -> pd.DataFrame:
    trials = pd.read_sql_query(
        """
        SELECT nct_id, brief_title, official_title, brief_summary, conditions,
               overall_status, lead_sponsor_class, lead_sponsor_name, phase,
               start_date, retrieved_at, source_id
        FROM trials
        """,
        conn,
    )
    interventions = pd.read_sql_query(
        """
        SELECT nct_id, intervention_type, intervention_name
        FROM trial_interventions
        """,
        conn,
    )
    if len(interventions):
        grouped = (
            interventions.groupby("nct_id")
            .agg(
                intervention_types=("intervention_type", lambda s: " | ".join(str(x) for x in s if pd.notna(x))),
                intervention_names=("intervention_name", lambda s: " | ".join(str(x) for x in s if pd.notna(x))),
            )
            .reset_index()
        )
        trials = trials.merge(grouped, on="nct_id", how="left")
    else:
        trials["intervention_types"] = ""
        trials["intervention_names"] = ""
    trials["intervention_types"] = trials["intervention_types"].fillna("")
    trials["intervention_names"] = trials["intervention_names"].fillna("")
    trials["ncfb_heuristic"] = trials.apply(
        lambda row: flag_ncfb(
            " ".join(
                str(row[col] or "")
                for col in ("brief_title", "official_title", "brief_summary", "conditions")
            )
        ),
        axis=1,
    )
    trials["is_active"] = trials["overall_status"].isin(ACTIVE_STATUSES)
    trials["normalized_stage"] = trials["phase"].map(lambda p: normalize_stage(p))
    return trials


def apply_trial_overrides(trials: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    overlay_cols = [
        "disease_area",
        "strategy",
        "need_ids",
        "role",
        "map_eligible",
        "whitespace_relevant",
        "crowding_unit",
        "asset_name",
        "company_name",
        "linked_program_id",
        "review_notes",
    ]
    suggested_rows = []
    for _, row in trials.iterrows():
        suggested = suggest_trial_row(
            _blob_from_trial(row),
            row.get("phase"),
            row.get("intervention_types") or "",
            row.get("ncfb_heuristic"),
        )
        suggested_rows.append(suggested)
    suggested = pd.DataFrame(suggested_rows)
    out = pd.concat([trials.reset_index(drop=True), suggested], axis=1)
    out["asset_name"] = ""
    out["company_name"] = out["lead_sponsor_name"].fillna("")
    out["linked_program_id"] = ""
    out["review_notes"] = ""

    override_map = overrides.set_index("nct_id") if len(overrides) else pd.DataFrame()
    for idx, row in out.iterrows():
        nct = row["nct_id"]
        if nct not in override_map.index:
            continue
        ov = override_map.loc[nct]
        if isinstance(ov, pd.DataFrame):
            ov = ov.iloc[0]
        for col in overlay_cols:
            value = str(ov.get(col, "") or "").strip()
            if value == "":
                continue
            if col in {"map_eligible", "whitespace_relevant", "crowding_unit"}:
                out.at[idx, col] = int(value)
            else:
                out.at[idx, col] = value
        out.at[idx, "review_status"] = "reviewed"
        out.at[idx, "review_source"] = "trial_review_overrides"
        if not out.at[idx, "need_ids"]:
            out.at[idx, "need_ids"] = NEED_BY_STRATEGY.get(out.at[idx, "strategy"], "")
        # Safety: unreviewed never happens here; NCFB cannot be map-eligible.
        if out.at[idx, "disease_area"] != "cf":
            out.at[idx, "map_eligible"] = 0
            out.at[idx, "whitespace_relevant"] = 0
            out.at[idx, "crowding_unit"] = 0
    out["map_eligible"] = pd.to_numeric(out["map_eligible"], errors="coerce").fillna(0).astype(int)
    out["whitespace_relevant"] = pd.to_numeric(out["whitespace_relevant"], errors="coerce").fillna(0).astype(int)
    out["crowding_unit"] = pd.to_numeric(out["crowding_unit"], errors="coerce").fillna(0).astype(int)
    auto = out["review_status"] == "auto_suggested"
    out.loc[auto, ["map_eligible", "whitespace_relevant", "crowding_unit"]] = 0
    return out


def classify_programs(programs: pd.DataFrame, reviews: pd.DataFrame) -> pd.DataFrame:
    merged = programs.merge(reviews, on="program_id", how="left", suffixes=("", "_review"))
    missing = merged["review_status_review"].isna() | (merged["review_status_review"] == "")
    if missing.any():
        ids = merged.loc[missing, "program_id"].tolist()
        raise ValueError(f"program_reviews.csv missing rows for: {ids}")
    out = pd.DataFrame(
        {
            "program_id": merged["program_id"],
            "asset_name": merged["asset_name"],
            "company_name": merged["company_name"],
            "cff_strategy": merged["therapeutic_strategy"],
            "cff_stage": merged["development_stage"],
            "cff_listed_status": merged["cff_listed_status"],
            "activity_status": merged["activity_status"],
            "disease_area": merged["disease_area"],
            "strategy": merged["strategy"].where(merged["strategy"] != "", merged["therapeutic_strategy"]),
            "need_ids": merged["need_ids"],
            "role": merged["role"],
            "map_eligible": pd.to_numeric(merged["map_eligible"], errors="coerce").fillna(0).astype(int),
            "whitespace_relevant": pd.to_numeric(merged["whitespace_relevant"], errors="coerce").fillna(0).astype(int),
            "crowding_unit": pd.to_numeric(merged["crowding_unit"], errors="coerce").fillna(0).astype(int),
            "nct_ids": merged["nct_ids"],
            "normalized_stage": [
                normalize_stage(None, stage)
                for stage in merged["map_stage"].where(merged["map_stage"] != "", merged["development_stage"])
            ],
            "review_status": merged["review_status_review"],
            "review_notes": merged["review_notes"],
            "source_id": merged["source_id"],
        }
    )
    not_cf = out["disease_area"] != "cf"
    out.loc[not_cf, ["map_eligible", "whitespace_relevant", "crowding_unit"]] = 0
    return out


def map_eligible_mask(frame: pd.DataFrame) -> pd.Series:
    return (
        (frame["review_status"] == "reviewed")
        & (frame["disease_area"] == "cf")
        & (frame["map_eligible"] == 1)
    )


def build_map_assets(programs: pd.DataFrame, trials: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    linked_ncts: set[str] = set()

    for _, prog in programs.iterrows():
        if not (
            prog["review_status"] == "reviewed"
            and prog["disease_area"] == "cf"
            and int(prog["map_eligible"]) == 1
        ):
            continue
        nct_ids = [p.strip() for p in str(prog["nct_ids"] or "").split(";") if p.strip()]
        linked_ncts.update(nct_ids)
        trial_hits = trials.loc[trials["nct_id"].isin(nct_ids)]
        stage = prog["normalized_stage"]
        if prog["activity_status"] in {"approved", "standard_of_care"}:
            stage = normalize_stage(None, prog["activity_status"])
        elif len(trial_hits):
            # Prefer the latest clinical stage among linked CF trials.
            stages = [normalize_stage(p) for p in trial_hits["phase"].tolist()]
            for candidate in ("phase_3", "phase_2", "phase_1"):
                if candidate in stages:
                    stage = candidate
                    break
        rows.append(
            {
                "asset_id": prog["program_id"],
                "asset_name": prog["asset_name"],
                "company_name": prog["company_name"],
                "source": "cff_pipeline",
                "strategy": prog["strategy"],
                "need_ids": prog["need_ids"] or NEED_BY_STRATEGY.get(prog["strategy"], ""),
                "role": prog["role"],
                "stage": stage,
                "activity_status": prog["activity_status"],
                "sponsor_class": _sponsor_class(prog["company_name"], trial_hits),
                "nct_ids": ";".join(nct_ids),
                "map_eligible": 1,
                "whitespace_relevant": int(prog["whitespace_relevant"]),
                "crowding_unit": int(prog["crowding_unit"]),
                "review_status": "reviewed",
                "review_notes": prog["review_notes"],
            }
        )

    trial_map = trials.loc[map_eligible_mask(trials)].copy()
    for _, trial in trial_map.iterrows():
        linked = str(trial.get("linked_program_id") or "").strip()
        if linked or trial["nct_id"] in linked_ncts:
            continue
        rows.append(
            {
                "asset_id": f"trial:{trial['nct_id']}",
                "asset_name": trial.get("asset_name") or trial["brief_title"],
                "company_name": trial.get("company_name") or trial["lead_sponsor_name"],
                "source": "clinicaltrials",
                "strategy": trial["strategy"],
                "need_ids": trial["need_ids"],
                "role": trial["role"],
                "stage": trial["normalized_stage"],
                "activity_status": "active_clinical",
                "sponsor_class": "INDUSTRY" if trial["lead_sponsor_class"] == "INDUSTRY" else "ACADEMIC_OR_OTHER",
                "nct_ids": trial["nct_id"],
                "map_eligible": 1,
                "whitespace_relevant": int(trial["whitespace_relevant"]),
                "crowding_unit": int(trial["crowding_unit"]),
                "review_status": "reviewed",
                "review_notes": trial.get("review_notes") or "",
            }
        )

    assets = pd.DataFrame(rows)
    if len(assets) == 0:
        return assets
    if not (assets["review_status"] == "reviewed").all():
        raise AssertionError("map_assets contains a non-reviewed row")
    if not (assets["map_eligible"] == 1).all():
        raise AssertionError("map_assets contains a non-eligible row")
    return assets.sort_values(["strategy", "stage", "asset_id"]).reset_index(drop=True)


def _sponsor_class(company_name: object, trial_hits: pd.DataFrame) -> str:
    if len(trial_hits) and (trial_hits["lead_sponsor_class"] == "INDUSTRY").any():
        return "INDUSTRY"
    if company_name is None or (isinstance(company_name, float) and pd.isna(company_name)):
        name = ""
    else:
        name = str(company_name).strip().lower()
    if name in {"", "generic", "multiple"}:
        return "SOC_OR_GENERIC"
    academic_markers = ("university", "hospital", "foundation", "research")
    if any(marker in name for marker in academic_markers) and "sionna" not in name:
        return "ACADEMIC_OR_OTHER"
    return "INDUSTRY"


def build_competitive_map(assets: pd.DataFrame) -> pd.DataFrame:
    if len(assets) == 0:
        return pd.DataFrame()
    counted = assets.loc[assets["crowding_unit"] == 1].copy()
    counted["stage"] = pd.Categorical(counted["stage"], categories=list(STAGE_ORDER), ordered=True)
    grouped = (
        counted.groupby(["strategy", "stage"], observed=False)
        .agg(
            n_assets=("asset_id", "size"),
            n_industry=("sponsor_class", lambda s: int((s == "INDUSTRY").sum())),
            n_academic=("sponsor_class", lambda s: int((s == "ACADEMIC_OR_OTHER").sum())),
            n_whitespace=("whitespace_relevant", "sum"),
        )
        .reset_index()
    )
    grouped = grouped.loc[grouped["n_assets"] > 0].copy()
    totals = counted.groupby("strategy").size().to_dict()
    grouped["strategy_total"] = grouped["strategy"].map(totals)
    grouped["crowding_band"] = grouped["strategy_total"].map(lambda n: crowding_band(int(n)))
    grouped["universe"] = "reviewed_map_eligible_crowding_unit"
    grouped["source_id"] = SOURCE_ID
    return grouped.sort_values(["strategy", "stage"])


def build_need_coverage(assets: pd.DataFrame, trials: pd.DataFrame, needs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    counted = assets.loc[assets["crowding_unit"] == 1] if len(assets) else assets
    for _, need in needs.iterrows():
        nid = need["need_id"]
        all_hits = assets.loc[assets["need_ids"].fillna("").str.contains(nid, regex=False)] if len(assets) else assets
        asset_hits = counted.loc[counted["need_ids"].fillna("").str.contains(nid, regex=False)] if len(counted) else counted
        industry = asset_hits.loc[asset_hits["sponsor_class"] == "INDUSTRY"] if len(asset_hits) else asset_hits
        whitespace_ind = (
            industry.loc[industry["whitespace_relevant"] == 1] if len(industry) else industry
        )
        reviewed_trials = trials.loc[
            (trials["review_status"] == "reviewed")
            & (trials["disease_area"] == "cf")
            & (trials["need_ids"].fillna("").str.contains(nid, regex=False))
            & (trials["is_active"])
        ]
        auto_active = trials.loc[
            (trials["review_status"] == "auto_suggested")
            & (trials["need_ids"].fillna("").str.contains(nid, regex=False))
            & (trials["is_active"])
            & (trials["ncfb_heuristic"].isna() | (trials["ncfb_heuristic"] == ""))
        ]
        n_ws = int(len(whitespace_ind)) if len(asset_hits) else 0
        rows.append(
            {
                "need_id": nid,
                "category": need["category"],
                "subcategory": need["subcategory"],
                "n_map_assets": int(len(all_hits)) if len(assets) else 0,
                "n_crowding_units": int(len(asset_hits)) if len(counted) else 0,
                "n_industry_map_assets": int(len(industry)) if len(asset_hits) else 0,
                "n_industry_whitespace": n_ws,
                "n_academic_map_assets": int((all_hits["sponsor_class"] == "ACADEMIC_OR_OTHER").sum())
                if len(all_hits)
                else 0,
                "n_reviewed_active_cf_trials": int(len(reviewed_trials)),
                "n_auto_suggested_active_cf_like": int(len(auto_active)),
                "crowding_band": crowding_band(n_ws),
                "notes": (
                    "n_map_assets is every reviewed CF map-eligible row tagged to the need. "
                    "n_industry_whitespace and crowding_band use crowding_unit=1 only. "
                    "Auto-suggested active counts are context only and must not be ranked."
                ),
            }
        )
    return pd.DataFrame(rows)


def classification_summary(trials: pd.DataFrame, programs: pd.DataFrame, assets: pd.DataFrame) -> pd.DataFrame:
    incretin = trials.loc[trials["nct_id"] == "NCT01851694"]
    incretin_area = incretin["disease_area"].iloc[0] if len(incretin) else ""
    rows = [
        ("trials_total", len(trials), "All interventional CF-tagged studies in the snapshot"),
        ("trials_reviewed", int((trials["review_status"] == "reviewed").sum()), "Manual overlay applied"),
        ("trials_auto_suggested", int((trials["review_status"] == "auto_suggested").sum()), "Keyword suggestion only"),
        (
            "trials_map_eligible",
            int(map_eligible_mask(trials).sum()),
            "Reviewed + disease_area=cf + map_eligible=1",
        ),
        (
            "ncfb_heuristic_flagged",
            int(trials["ncfb_heuristic"].fillna("").ne("").sum()),
            "Phase 3 title/summary heuristic",
        ),
        (
            "nct01851694_disease_area",
            1 if incretin_area == "cf" else 0,
            f"Override must classify this CFRD study as cf; current={incretin_area}",
        ),
        ("programs_reviewed", int((programs["review_status"] == "reviewed").sum()), "Every CFF pipeline row"),
        ("map_assets", len(assets), "Reviewed CF map-eligible programs and unmatched trials"),
        (
            "map_assets_whitespace",
            int(assets["whitespace_relevant"].sum()) if len(assets) else 0,
            "Investigational (not approved/SOC label expansions)",
        ),
    ]
    return pd.DataFrame(rows, columns=["metric", "value_numeric", "notes"])


def write_tables(tables: dict[str, pd.DataFrame], destination: Path | None = None) -> Path:
    out = destination or (processed_dir() / "classification")
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    return out


def write_figures(assets: pd.DataFrame, coverage: pd.DataFrame, destination: Path | None = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig_dir = destination or (repo_root() / "assets" / "figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    color = "#1f4e5f"
    color_b = "#8a9aa3"

    def save(fig, name: str) -> None:
        fig.tight_layout()
        fig.savefig(fig_dir / name, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    counted = assets.loc[assets["crowding_unit"] == 1].copy() if len(assets) else assets
    strategies = sorted(counted["strategy"].unique()) if len(counted) else []
    stages = ["preclinical", "phase_1", "phase_2", "phase_3", "approved", "standard_of_care"]
    if strategies:
        matrix = np.zeros((len(strategies), len(stages)))
        for i, strategy in enumerate(strategies):
            for j, stage in enumerate(stages):
                matrix[i, j] = int(
                    ((counted["strategy"] == strategy) & (counted["stage"] == stage)).sum()
                )
        fig, ax = plt.subplots(figsize=(9.2, max(3.8, 0.38 * len(strategies) + 1.8)))
        im = ax.imshow(matrix, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(["Preclinical", "Ph1", "Ph2", "Ph3", "Approved", "SoC"], rotation=0)
        ax.set_yticks(range(len(strategies)))
        ax.set_yticklabels(strategies)
        ax.set_title("Reviewed CF map assets by strategy and stage")
        for i in range(len(strategies)):
            for j in range(len(stages)):
                val = int(matrix[i, j])
                if val:
                    ax.text(j, i, str(val), ha="center", va="center", color="#111111", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        fig.text(
            0.01,
            -0.04,
            "ANALYSIS. Reviewed, CF, map-eligible, crowding_unit=1 only. Source: ClinicalTrials.gov snapshot 2026-09-09 plus CFF pipeline overlay.",
            fontsize=8,
            color="#444444",
        )
        save(fig, "competitive_map_strategy_stage.png")

    if len(coverage):
        fig, ax = plt.subplots(figsize=(8.6, 4.6))
        labels = coverage["need_id"].tolist()
        industry = coverage["n_industry_whitespace"].tolist()
        academic = coverage["n_academic_map_assets"].tolist()
        x = range(len(labels))
        ax.bar(x, industry, color=color, label="Industry investigational (whitespace flag)")
        ax.bar(x, academic, bottom=industry, color=color_b, label="Academic/other map assets")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_title("Reviewed pipeline coverage by unmet-need category")
        ax.set_ylabel("Map assets")
        ax.set_xlabel("Need ID")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False)
        fig.text(
            0.01,
            -0.06,
            "ANALYSIS. Industry whitespace = reviewed investigational CF assets, crowding_unit=1. Academic bars include non-industry map assets (approved/SOC excluded from the industry series).",
            fontsize=8,
            color="#444444",
        )
        save(fig, "need_pipeline_coverage.png")
    return fig_dir


def run_classify(db_path: Path | None = None) -> dict[str, str | int]:
    conn = connect(db_path)
    try:
        trials_raw = trial_frame(conn)
        programs_raw = pd.read_sql_query("SELECT * FROM programs", conn)
        needs = pd.read_sql_query(
            "SELECT need_id, category, subcategory FROM unmet_needs ORDER BY need_id",
            conn,
        )
    finally:
        conn.close()

    overrides = _load_csv(external_dir() / "trial_review_overrides.csv")
    reviews = _load_csv(external_dir() / "program_reviews.csv")
    trials = apply_trial_overrides(trials_raw, overrides)
    programs = classify_programs(programs_raw, reviews)
    assets = build_map_assets(programs, trials)
    competitive = build_competitive_map(assets)
    coverage = build_need_coverage(assets, trials, needs)
    summary = classification_summary(trials, programs, assets)

    trial_cols = [
        "nct_id",
        "brief_title",
        "overall_status",
        "lead_sponsor_class",
        "lead_sponsor_name",
        "phase",
        "normalized_stage",
        "is_active",
        "ncfb_heuristic",
        "disease_area",
        "strategy",
        "strategy_rule_id",
        "need_ids",
        "role",
        "map_eligible",
        "whitespace_relevant",
        "crowding_unit",
        "review_status",
        "review_source",
        "asset_name",
        "company_name",
        "linked_program_id",
        "review_notes",
        "retrieved_at",
        "source_id",
    ]
    tables = {
        "trial_classifications": trials[trial_cols],
        "program_classifications": programs,
        "map_assets": assets,
        "competitive_map": competitive,
        "need_pipeline_coverage": coverage,
        "classification_summary": summary,
    }
    out_tables = write_tables(tables)
    out_figs = write_figures(assets, coverage)
    return {
        "tables_dir": str(out_tables),
        "figures_dir": str(out_figs),
        "trials": int(len(trials)),
        "reviewed_trials": int((trials["review_status"] == "reviewed").sum()),
        "map_assets": int(len(assets)),
        "nct01851694_cf": int(
            (
                (trials["nct_id"] == "NCT01851694")
                & (trials["disease_area"] == "cf")
                & (trials["review_status"] == "reviewed")
            ).sum()
        ),
    }
