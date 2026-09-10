"""Phase 3 landscape analysis: cited patient and pipeline facts."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

from cf_atlas.paths import processed_dir, repo_root, sqlite_path

ACTIVE_STATUSES = (
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
)

NCFB_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"non[\s-]*cystic\s+fibrosis\s+bronchiectasis", re.I),
        "non-cystic fibrosis bronchiectasis",
    ),
    (re.compile(r"non[\s-]*cf[\s-]*bronchiectasis", re.I), "non-cf bronchiectasis"),
    (re.compile(r"\bncfb\b", re.I), "ncfb"),
    (re.compile(r"\bnon-cfb\b", re.I), "non-cfb"),
    (re.compile(r"non[\s-]*cystic\s+fibrosis", re.I), "non-cystic fibrosis phrase"),
]


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or sqlite_path()
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run `python -m cf_atlas build-db` first.")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def flag_ncfb(text: str) -> str | None:
    """Return a reason string if the record likely is non-CF bronchiectasis tagging noise."""
    for pattern, label in NCFB_PATTERNS:
        if pattern.search(text or ""):
            return label
    return None


def _blob(row: sqlite3.Row) -> str:
    parts = [
        row["brief_title"],
        row["official_title"],
        row["brief_summary"],
        row["conditions"],
    ]
    return " ".join(str(p) for p in parts if p)


def stat(
    conn: sqlite3.Connection,
    metric_key: str,
    year: int,
    stratum: str,
) -> sqlite3.Row:
    row = conn.execute(
        """
        SELECT * FROM registry_stats
        WHERE metric_key = ? AND year = ? AND stratum = ?
        """,
        (metric_key, year, stratum),
    ).fetchone()
    if row is None:
        raise KeyError(f"No registry_stats row for {metric_key} {year} {stratum}")
    return row


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
    trials["ncfb_reason"] = (_blob_series(trials)).map(flag_ncfb)
    trials["is_likely_ncfb"] = trials["ncfb_reason"].notna()
    trials["start_year"] = trials["start_date"].str.slice(0, 4)
    trials["is_active"] = trials["overall_status"].isin(ACTIVE_STATUSES)
    return trials


def _blob_series(trials: pd.DataFrame) -> pd.Series:
    return (
        trials["brief_title"].fillna("")
        + " "
        + trials["official_title"].fillna("")
        + " "
        + trials["brief_summary"].fillna("")
        + " "
        + trials["conditions"].fillna("")
    )


def build_tables(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    trials = trial_frame(conn)
    cf_like = trials.loc[~trials["is_likely_ncfb"]].copy()
    retrieved = str(trials["retrieved_at"].dropna().iloc[0]) if len(trials) else ""

    by_year = (
        trials.groupby("start_year", dropna=False)
        .agg(
            n_all=("nct_id", "size"),
            n_likely_ncfb=("is_likely_ncfb", "sum"),
        )
        .reset_index()
    )
    by_year["n_cf_like"] = by_year["n_all"] - by_year["n_likely_ncfb"]
    by_year["source_id"] = "clinicaltrials_gov_api_v2"

    by_status = (
        trials.groupby(["overall_status", "is_likely_ncfb"], dropna=False)
        .size()
        .reset_index(name="n")
    )
    by_status["source_id"] = "clinicaltrials_gov_api_v2"

    by_phase = (
        cf_like.assign(phase=cf_like["phase"].fillna("NA"))
        .groupby("phase")
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )
    by_phase["universe"] = "cf_like_excluding_ncfb_heuristic"
    by_phase["source_id"] = "clinicaltrials_gov_api_v2"

    by_sponsor = (
        cf_like.groupby("lead_sponsor_class", dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )
    by_sponsor["universe"] = "cf_like_excluding_ncfb_heuristic"
    by_sponsor["source_id"] = "clinicaltrials_gov_api_v2"

    ncfb_flagged = trials.loc[
        trials["is_likely_ncfb"],
        [
            "nct_id",
            "brief_title",
            "overall_status",
            "lead_sponsor_class",
            "phase",
            "start_date",
            "ncfb_reason",
        ],
    ].sort_values("nct_id")

    claims = _claims(conn, trials, cf_like, retrieved)
    solved = _solved_unsolved(conn)
    needs = _need_snapshots(conn)

    return {
        "trials_by_year": by_year,
        "trials_by_status": by_status,
        "trials_by_phase_cf_like": by_phase,
        "trials_by_sponsor_class_cf_like": by_sponsor,
        "ncfb_flagged_trials": ncfb_flagged,
        "landscape_claims": claims,
        "solved_unsolved": solved,
        "need_snapshots": needs,
    }


def _claims(
    conn: sqlite3.Connection,
    trials: pd.DataFrame,
    cf_like: pd.DataFrame,
    retrieved: str,
) -> pd.DataFrame:
    def r(metric: str, year: int, stratum: str) -> sqlite3.Row:
        return stat(conn, metric, year, stratum)

    people_2024 = r("registry.people_with_cf", 2024, "all")
    survival_2009 = r("registry.predicted_median_survival", 2009, "all")
    survival_2024 = r("registry.predicted_median_survival", 2024, "all")
    adults_1994 = r("registry.adults_pct", 1994, "age_ge_18")
    adults_2024 = r("registry.adults_pct", 2024, "age_ge_18")
    pa_2009 = r("registry.pseudomonas_pct", 2009, "cultured")
    pa_2024 = r("registry.pseudomonas_pct", 2024, "cultured")
    pex_2009 = r("registry.pex_iv_pct", 2009, "all")
    pex_2024 = r("registry.pex_iv_pct", 2024, "all")
    fev1_2009 = r("registry.fev1_pct_predicted", 2009, "age_gt_7")
    fev1_2024 = r("registry.fev1_pct_predicted", 2024, "age_gt_7")
    tx_2019 = r("registry.lung_transplants", 2019, "all")
    tx_2024 = r("registry.lung_transplants", 2024, "all")
    eligible = r("registry.modulator_eligible_pct", 2024, "all")
    ineligible = r("registry.modulator_ineligible_n", 2024, "all")
    ineligible_12 = r(
        "registry.modulator_ineligible_with_data_n", 2024, "age_ge_12_no_lung_transplant"
    )
    not_rx = r("registry.eligible_not_prescribed_n", 2024, "age_ge_12_in_2020")
    cfrd_all = r("registry.cfrd_pct", 2024, "complications_no_lung_transplant")
    cfrd_adult = r("registry.cfrd_pct", 2024, "age_ge_18_no_lung_transplant")
    pert = r("registry.pert_pct", 2024, "all")
    dornase = r("registry.dornase_pct", 2024, "age_ge_6")
    hs = r("registry.hypertonic_saline_pct", 2024, "age_ge_6")
    age60 = r("registry.people_with_cf", 2024, "age_ge_60")
    anxiety_ad = r("registry.anxiety_pct", 2024, "age_ge_18_mental_health")
    dep_ad = r("registry.depression_pct", 2024, "age_ge_18_mental_health")
    cirrhosis = r("registry.liver_cirrhosis_pct", 2024, "complications_no_lung_transplant")
    visits_2019 = r("registry.clinic_visits_mean", 2019, "all")
    visits_2024 = r("registry.clinic_visits_mean", 2024, "all")
    modulator_ge12 = r("registry.modulator_prescribed_pct", 2024, "age_ge_12")
    ntm = r("registry.ntm_pct", 2024, "mycobacterial_culture")
    ntm60 = r("registry.ntm_pct", 2024, "age_ge_60")
    fev1_4059 = r("registry.fev1_pct_predicted", 2024, "age_40_49")

    n_all = len(trials)
    n_ncfb = int(trials["is_likely_ncfb"].sum())
    n_cf = len(cf_like)
    n_recruiting = int((trials["overall_status"] == "RECRUITING").sum())
    n_recruiting_cf = int((cf_like["overall_status"] == "RECRUITING").sum())
    n_active_cf = int(cf_like["is_active"].sum())
    n_industry_recruit_cf = int(
        (
            (cf_like["overall_status"] == "RECRUITING")
            & (cf_like["lead_sponsor_class"] == "INDUSTRY")
        ).sum()
    )
    n_other_recruit_cf = int(
        (
            (cf_like["overall_status"] == "RECRUITING")
            & (cf_like["lead_sponsor_class"] == "OTHER")
        ).sum()
    )
    started_2015 = int((trials["start_year"] == "2015").sum())
    started_2024 = int((trials["start_year"] == "2024").sum())
    started_2026 = int((trials["start_year"] == "2026").sum())

    rows = [
        {
            "claim_id": "C001",
            "layer": "fact",
            "need_id": "",
            "statement": "People with CF in the 2024 CFF Patient Registry",
            "value_numeric": people_2024["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": people_2024["source_id"],
            "stat_id": people_2024["stat_id"],
            "notes": people_2024["population_notes"],
        },
        {
            "claim_id": "C002",
            "layer": "fact",
            "need_id": "N7",
            "statement": "Predicted median survival rose from 38.0 years (2009) to 65.4 years (2024)",
            "value_numeric": survival_2024["value_numeric"],
            "unit": "years",
            "year": 2024,
            "source_id": survival_2024["source_id"],
            "stat_id": survival_2024["stat_id"],
            "notes": f"2009 value {survival_2009['value_numeric']}; 95% CI in 2024 was 63.6-68.1.",
        },
        {
            "claim_id": "C003",
            "layer": "fact",
            "need_id": "N7",
            "statement": "Adults aged 18+ as a share of the Registry",
            "value_numeric": adults_2024["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": adults_2024["source_id"],
            "stat_id": adults_2024["stat_id"],
            "notes": f"Was {adults_1994['value_numeric']}% in 1994.",
        },
        {
            "claim_id": "C004",
            "layer": "fact",
            "need_id": "N1",
            "statement": "Share eligible for at least one CFTR modulator after Alyftrek approval",
            "value_numeric": eligible["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": eligible["source_id"],
            "stat_id": eligible["stat_id"],
            "notes": eligible["population_notes"],
        },
        {
            "claim_id": "C005",
            "layer": "fact",
            "need_id": "N1",
            "statement": "Ineligible for a CFTRm by age or CFTR genotype",
            "value_numeric": ineligible["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": ineligible["source_id"],
            "stat_id": ineligible["stat_id"],
            "notes": ineligible["denominator_notes"],
        },
        {
            "claim_id": "C006",
            "layer": "fact",
            "need_id": "N1",
            "statement": "Modulator-ineligible adolescents and adults with Registry data",
            "value_numeric": ineligible_12["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": ineligible_12["source_id"],
            "stat_id": ineligible_12["stat_id"],
            "notes": ineligible_12["population_notes"],
        },
        {
            "claim_id": "C007",
            "layer": "fact",
            "need_id": "N2",
            "statement": "Aged 12+ in 2020 and eligible then, with no CFTRm prescription 2022-2024",
            "value_numeric": not_rx["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": not_rx["source_id"],
            "stat_id": not_rx["stat_id"],
            "notes": not_rx["population_notes"],
        },
        {
            "claim_id": "C008",
            "layer": "fact",
            "need_id": "N1",
            "statement": "Prescribed a modulator among ages 12+",
            "value_numeric": modulator_ge12["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": modulator_ge12["source_id"],
            "stat_id": modulator_ge12["stat_id"],
            "notes": "",
        },
        {
            "claim_id": "C009",
            "layer": "fact",
            "need_id": "N3",
            "statement": "Mean FEV1 percent predicted among ages >7",
            "value_numeric": fev1_2024["value_numeric"],
            "unit": "percent_predicted",
            "year": 2024,
            "source_id": fev1_2024["source_id"],
            "stat_id": fev1_2024["stat_id"],
            "notes": f"Was {fev1_2009['value_numeric']} in 2009. Ages 40-49 mean is {fev1_4059['value_numeric']}.",
        },
        {
            "claim_id": "C010",
            "layer": "fact",
            "need_id": "N3",
            "statement": "Treated with IV antibiotics for a pulmonary exacerbation",
            "value_numeric": pex_2024["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": pex_2024["source_id"],
            "stat_id": pex_2024["stat_id"],
            "notes": f"Was {pex_2009['value_numeric']}% in 2009.",
        },
        {
            "claim_id": "C011",
            "layer": "fact",
            "need_id": "N3",
            "statement": "Lung transplants (all procedures) in the reporting year",
            "value_numeric": tx_2024["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": tx_2024["source_id"],
            "stat_id": tx_2024["stat_id"],
            "notes": f"Was {tx_2019['value_numeric']} in 2019.",
        },
        {
            "claim_id": "C012",
            "layer": "fact",
            "need_id": "N4",
            "statement": "Pseudomonas aeruginosa in any culture",
            "value_numeric": pa_2024["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": pa_2024["source_id"],
            "stat_id": pa_2024["stat_id"],
            "notes": f"Was {pa_2009['value_numeric']}% in 2009. Fewer cultures since 2020 affect ascertainment.",
        },
        {
            "claim_id": "C013",
            "layer": "fact",
            "need_id": "N4",
            "statement": "Mycobacterial species among those with a mycobacterial culture",
            "value_numeric": ntm["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": ntm["source_id"],
            "stat_id": ntm["stat_id"],
            "notes": f"Ages 60+ : {ntm60['value_numeric']}%.",
        },
        {
            "claim_id": "C014",
            "layer": "fact",
            "need_id": "N5",
            "statement": "CFRD prevalence in the complications population (transplant-censored)",
            "value_numeric": cfrd_all["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": cfrd_all["source_id"],
            "stat_id": cfrd_all["stat_id"],
            "notes": f"Adults {cfrd_adult['value_numeric']}%. Denominator is not the full 33989 demographic total.",
        },
        {
            "claim_id": "C015",
            "layer": "fact",
            "need_id": "N6",
            "statement": "Pancreatic enzyme replacement therapy",
            "value_numeric": pert["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": pert["source_id"],
            "stat_id": pert["stat_id"],
            "notes": "",
        },
        {
            "claim_id": "C016",
            "layer": "fact",
            "need_id": "N6",
            "statement": "Liver disease, cirrhosis, in the complications population",
            "value_numeric": cirrhosis["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": cirrhosis["source_id"],
            "stat_id": cirrhosis["stat_id"],
            "notes": "",
        },
        {
            "claim_id": "C017",
            "layer": "fact",
            "need_id": "N7",
            "statement": "People with CF aged 60 and older",
            "value_numeric": age60["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": age60["source_id"],
            "stat_id": age60["stat_id"],
            "notes": age60["population_notes"],
        },
        {
            "claim_id": "C018",
            "layer": "fact",
            "need_id": "N7",
            "statement": "Anxiety disorder among adults",
            "value_numeric": anxiety_ad["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": anxiety_ad["source_id"],
            "stat_id": anxiety_ad["stat_id"],
            "notes": f"Adult depression {dep_ad['value_numeric']}%.",
        },
        {
            "claim_id": "C019",
            "layer": "fact",
            "need_id": "N8",
            "statement": "Mean outpatient CF center visits per year",
            "value_numeric": visits_2024["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": visits_2024["source_id"],
            "stat_id": visits_2024["stat_id"],
            "notes": f"Was {visits_2019['value_numeric']} in 2019. Dornase {dornase['value_numeric']}% and hypertonic saline {hs['value_numeric']}% among ages >=6.",
        },
        {
            "claim_id": "C020",
            "layer": "analysis",
            "need_id": "",
            "statement": "Interventional ClinicalTrials.gov records tagged to cystic fibrosis",
            "value_numeric": n_all,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": f"Retrieved {retrieved}. Sponsor-reported. Includes studies that mention CF without CF being the intended disease.",
        },
        {
            "claim_id": "C021",
            "layer": "analysis",
            "need_id": "",
            "statement": "Records flagged as likely non-CF bronchiectasis / non-cystic fibrosis tagging noise",
            "value_numeric": n_ncfb,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": "Heuristic on title, official title, summary, and conditions. Not a reviewed classification. See ncfb_flagged_trials.csv.",
        },
        {
            "claim_id": "C022",
            "layer": "analysis",
            "need_id": "",
            "statement": "CF-like interventional records after NCFB heuristic exclusion",
            "value_numeric": n_cf,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": "Remainder can still include non-CF muco-obstructive or mixed-disease studies.",
        },
        {
            "claim_id": "C023",
            "layer": "analysis",
            "need_id": "",
            "statement": "Recruiting CF-like interventional studies",
            "value_numeric": n_recruiting_cf,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": f"{n_recruiting} recruiting in the unfiltered CF-tagged set. Industry {n_industry_recruit_cf}; class OTHER {n_other_recruit_cf}.",
        },
        {
            "claim_id": "C024",
            "layer": "analysis",
            "need_id": "",
            "statement": "Active-like CF-like studies (recruiting, not yet recruiting, active not recruiting, enrolling by invitation)",
            "value_numeric": n_active_cf,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": "",
        },
        {
            "claim_id": "C025",
            "layer": "analysis",
            "need_id": "",
            "statement": "Interventional CF-tagged studies with start year 2015 (peak in this snapshot)",
            "value_numeric": started_2015,
            "unit": "count",
            "year": 2015,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": f"2024 starts: {started_2024}. 2026 starts: {started_2026} (partial calendar year as of retrieval).",
        },
        {
            "claim_id": "C026",
            "layer": "interpretation",
            "need_id": "N1",
            "statement": "Modulators have reached most US Registry patients, but a four-digit ineligible group and a three-digit eligible-not-prescribed group remain visible in published aggregates",
            "value_numeric": ineligible["value_numeric"],
            "unit": "count",
            "year": 2024,
            "source_id": ineligible["source_id"],
            "stat_id": ineligible["stat_id"],
            "notes": "Interpretation of C005 and C007 together. Not a TAM.",
        },
        {
            "claim_id": "C027",
            "layer": "interpretation",
            "need_id": "N3",
            "statement": "Pulmonary outcomes improved sharply after modulators, but exacerbations, advanced lung disease, and lower FEV1 in older adults show residual lung disease is not solved",
            "value_numeric": pex_2024["value_numeric"],
            "unit": "percent",
            "year": 2024,
            "source_id": pex_2024["source_id"],
            "stat_id": pex_2024["stat_id"],
            "notes": "Do not read mean FEV1 89.1% as absence of a pulmonary problem.",
        },
        {
            "claim_id": "C028",
            "layer": "hypothesis",
            "need_id": "",
            "statement": "Industry recruiting activity in the raw CF-tagged set is inflated by non-CF bronchiectasis programs; whitespace conclusions must use a reviewed CF universe",
            "value_numeric": n_ncfb,
            "unit": "count",
            "year": 2026,
            "source_id": "clinicaltrials_gov_api_v2",
            "stat_id": "",
            "notes": "Hypothesis for Phase 4 classification. Heuristic only.",
        },
    ]
    return pd.DataFrame(rows)


def _solved_unsolved(conn: sqlite3.Connection) -> pd.DataFrame:
    rows = [
        {
            "domain": "CFTR function",
            "need_id": "N1;N2",
            "solved_fact": "After Alyftrek, CFF estimates ~92% of people with CF are eligible for at least one modulator. Among ages 12+, 87.5% were prescribed a modulator in 2024.",
            "remains_fact": "2,434 people were ineligible by age or genotype; 1,226 ineligible adolescents/adults had Registry data. 623 people aged 12+ in 2020 had no CFTRm prescription in 2022-2024.",
            "interpretation": "Protein modulation is the solved core for most US patients. Remaining causal CFTR restoration is concentrated in no-protein / poorly responsive genotypes plus a smaller mixed access/tolerability group.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "Survival and demography",
            "need_id": "N7",
            "solved_fact": "Predicted median survival rose from 38.0 years (2009) to 65.4 (2024). Adults are 61.6% of the Registry, versus 33.8% in 1994. People aged 60+ number 1,437.",
            "remains_fact": "226 deaths were still reported in 2024. Median age at death was 38.8 years. Adult anxiety 31.9% and depression 30.2%. Osteopenia 19.4% of adults.",
            "interpretation": "CF is now an adult and increasingly older-adult disease in US care centers. That shift creates screening, metabolic, malignancy, and care-delivery questions; it does not by itself identify a biotech company.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "Pulmonary exacerbations and lung function",
            "need_id": "N3",
            "solved_fact": "IV-treated pulmonary exacerbations fell from 35.8% (2009) to 12.1% (2024). Mean FEV1 rose from 79.0% to 89.1% predicted among ages >7.",
            "remains_fact": "Exacerbations did not reach zero. Mean FEV1 among ages 40-49 was 72.8% predicted. Lung transplants fell from 249 (2019) to 61 (2024), not to zero. Dornase alfa remained at 80.6% of ages >=6.",
            "interpretation": "Highly effective modulators reduced pulmonary crisis rates. Residual lung disease, airway clearance burden, and advanced disease still exist and may be a crowded symptomatic-pipeline space.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "Chronic airway infection",
            "need_id": "N4",
            "solved_fact": "P. aeruginosa prevalence among cultured patients fell from 52.0% (2009) to 23.3% (2024). MRSA fell from 24.0% to 13.1%.",
            "remains_fact": "Nearly one in four cultured patients still had PA. NTM was 11.6% of those with a mycobacterial culture and 18.7% among ages 60+. Inhaled tobramycin remained 51.2% of PA-positive ages >=6.",
            "interpretation": "Infection burden declined with modulators and possibly with fewer cultures. Persistent PA, NTM in older adults, and ongoing inhaled-antibiotic use keep infection on the unmet-need list.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "CFRD and metabolism",
            "need_id": "N5",
            "solved_fact": "CFRD is recognized, screened, and usually treated; ~58% of people with diabetes in the Registry used CGM. Insulin remains guideline standard of care.",
            "remains_fact": "CFRD prevalence was 19.2% in the transplant-censored complications population and 29.3% among adults. 16.4% of people with CFRD had no treatment noted. No CF-specific disease-modifying metabolic approval is in the MVP therapy table.",
            "interpretation": "High adult prevalence plus insulin-centric care is a burden fact. Whether that is a CF-specific drug opportunity is a Phase 4-7 question, not a 2024 Registry conclusion.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "GI disease and CF liver disease",
            "need_id": "N6",
            "solved_fact": "PERT products are approved and widely used. Tube feeding fell to 5.1% in 2024.",
            "remains_fact": "80.2% still used PERT. Cirrhosis 2.7% and non-cirrhotic liver disease 3.5% in the complications population. UDCA was prescribed in 10.1%; CFF recommends against routine UDCA to prevent advanced CFLD.",
            "interpretation": "Pancreatic enzyme replacement is solved as a product class but not as a disease. Advanced CFLD is smaller and severe. Endpoints and addressable population need diligence later.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "Treatment burden and care delivery",
            "need_id": "N8",
            "solved_fact": "Visit volume and some inhaled-therapy intensity declined after 2019. Telehealth exists (mean 0.4 visits in 2024).",
            "remains_fact": "People still averaged 3.0 clinic visits. Hypertonic saline 62.6% and dornase 80.6% among ages >=6. 60.4% saw a pharmacist. The population is now majority adult.",
            "interpretation": "Burden fell but did not disappear. This is the opening for services/digital theses, not a default therapeutic white space.",
            "source_ids": "cff_registry_adr_2024",
        },
        {
            "domain": "Clinical development activity",
            "need_id": "",
            "solved_fact": "ClinicalTrials.gov contains a large historical interventional corpus tagged to CF (1,209 records in this snapshot, retrieved 2026-09-09).",
            "remains_fact": "A heuristic flagged likely non-CF bronchiectasis tagging noise. Recruiting industry titles in the raw extract include multiple NCFB programs. 2026 start counts are a partial year.",
            "interpretation": "Do not rank competitive intensity from unfiltered condition search. Phase 4 must review CF versus NCFB versus other muco-obstructive studies before whitespace scoring.",
            "source_ids": "clinicaltrials_gov_api_v2",
        },
    ]
    return pd.DataFrame(rows)


def _need_snapshots(conn: sqlite3.Connection) -> pd.DataFrame:
    needs = pd.read_sql_query("SELECT need_id, category, subcategory FROM unmet_needs ORDER BY need_id", conn)
    anchors = {
        "N1": "Ineligible 2,434; ineligible 12+ with data 1,226; ~92% eligible after VTD; 87.5% of ages 12+ prescribed a modulator.",
        "N2": "623 people aged 12+ in 2020 with no CFTRm prescription 2022-2024. Mixed reasons; not equivalent to N1.",
        "N3": "IV PEx 12.1% (was 35.8% in 2009). Mean FEV1 89.1% overall vs 72.8% ages 40-49. 61 lung transplants (was 249 in 2019).",
        "N4": "PA 23.3% of cultured (was 52.0% in 2009). NTM 11.6% of mycobacterial cultures; 18.7% ages 60+.",
        "N5": "CFRD 19.2% complications population; 29.3% of adults. Insulin-centric SoC; 16.4% with CFRD had no treatment noted.",
        "N6": "PERT 80.2%. Cirrhosis 2.7%; non-cirrhotic liver disease 3.5%; UDCA 10.1%.",
        "N7": "Adults 61.6%; ages 60+ n=1,437; survival 65.4 years; adult anxiety 31.9%; adult depression 30.2%.",
        "N8": "Mean 3.0 clinic visits (4.3 in 2019). Dornase 80.6%; hypertonic saline 62.6% ages >=6.",
    }
    needs["cited_2024_anchor"] = needs["need_id"].map(anchors)
    needs["source_id"] = "cff_registry_adr_2024"
    needs["layer"] = "fact"
    return needs


def write_tables(tables: dict[str, pd.DataFrame], destination: Path | None = None) -> Path:
    out = destination or (processed_dir() / "landscape")
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    return out


def _style_axes(ax, ylabel: str, xlabel: str) -> None:
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", linewidth=0.6, alpha=0.7)


def write_figures(conn: sqlite3.Connection, trials: pd.DataFrame, destination: Path | None = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = destination or (repo_root() / "assets" / "figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    color = "#1f4e5f"
    color_b = "#8a9aa3"

    def save(fig, name: str) -> None:
        fig.tight_layout()
        fig.savefig(fig_dir / name, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    years = [2009, 2014, 2019, 2023, 2024]
    survival = [stat(conn, "registry.predicted_median_survival", y, "all")["value_numeric"] for y in years]
    people = [stat(conn, "registry.people_with_cf", y, "all")["value_numeric"] for y in years]
    adults_years = [1994, 2009, 2014, 2019, 2023, 2024]
    adults = [stat(conn, "registry.adults_pct", y, "age_ge_18")["value_numeric"] for y in adults_years]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    axes[0].plot(years, survival, marker="o", color=color, linewidth=2)
    axes[0].set_title("Predicted median survival (CFF Registry)")
    _style_axes(axes[0], "Years", "Reporting year")
    axes[1].plot(adults_years, adults, marker="o", color=color, linewidth=2)
    axes[1].set_title("Adults ≥18 as share of Registry")
    _style_axes(axes[1], "Percent", "Reporting year")
    fig.text(
        0.01,
        -0.02,
        "FACT. Source: CFF Patient Registry 2024 Annual Data Report. Survival uses five-year increments as published.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "survival_and_adults.png")

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(years, [p / 1000 for p in people], marker="o", color=color, linewidth=2)
    ax.set_title("People with CF in the US CFF Registry")
    _style_axes(ax, "People (thousands)", "Reporting year")
    fig.text(
        0.01,
        -0.04,
        "FACT. Source: CFF Patient Registry 2024 ADR summary table. US accredited care-center consenters.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "registry_population.png")

    pulm_years = [2009, 2019, 2024]
    pa = [stat(conn, "registry.pseudomonas_pct", y, "cultured")["value_numeric"] for y in pulm_years]
    pex = [stat(conn, "registry.pex_iv_pct", y, "all")["value_numeric"] for y in pulm_years]
    fev1 = [stat(conn, "registry.fev1_pct_predicted", y, "age_gt_7")["value_numeric"] for y in pulm_years]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    axes[0].plot(pulm_years, pa, marker="o", color=color, linewidth=2, label="P. aeruginosa % cultured")
    axes[0].plot(pulm_years, pex, marker="s", color=color_b, linewidth=2, label="IV-treated PEx %")
    axes[0].legend(frameon=False)
    axes[0].set_title("Infection and exacerbations")
    _style_axes(axes[0], "Percent", "Reporting year")
    axes[1].plot(pulm_years, fev1, marker="o", color=color, linewidth=2)
    axes[1].set_title("Mean FEV1 % predicted (ages >7)")
    _style_axes(axes[1], "Percent predicted", "Reporting year")
    fig.text(
        0.01,
        -0.02,
        "FACT. Source: CFF 2024 ADR. PA among cultured patients. FEV1 uses GLI 2022 race-neutral equations. Fewer visits since 2020 reduce culture/PFT ascertainment.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "pulmonary_and_infection.png")

    year_counts = (
        trials.dropna(subset=["start_year"])
        .loc[trials["start_year"].str.match(r"^20\d\d$")]
        .groupby(["start_year", "is_likely_ncfb"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=[False, True], fill_value=0)
    )
    year_counts = year_counts.loc[(year_counts.index >= "2008") & (year_counts.index <= "2026")]
    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    x = list(year_counts.index)
    ax.bar(x, year_counts[False], color=color, label="CF-like (not flagged)")
    ax.bar(x, year_counts[True], bottom=year_counts[False], color=color_b, label="Likely NCFB tagging noise")
    ax.legend(frameon=False)
    ax.set_title("Interventional studies by start year, CF-tagged ClinicalTrials.gov extract")
    _style_axes(ax, "Studies started", "Start year")
    ax.tick_params(axis="x", rotation=45)
    fig.text(
        0.01,
        -0.06,
        "ANALYSIS. Source: ClinicalTrials.gov API v2, interventional, query.cond=cystic fibrosis, retrieved 2026-09-09. 2026 is a partial year. NCFB flag is a title/summary heuristic, not a reviewed classification.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "trials_started_by_year.png")

    labels = [
        "Registry total",
        "Ages 40-49",
        "Ineligible (age or genotype)",
        "Ages 60+",
        "Ineligible 12+ with data",
        "Cirrhosis (complications table)",
        "Eligible 2020, no Rx 2022-24",
        "Lung transplants 2024",
    ]
    values = [
        stat(conn, "registry.people_with_cf", 2024, "all")["value_numeric"],
        stat(conn, "registry.people_with_cf", 2024, "age_40_49")["value_numeric"],
        stat(conn, "registry.modulator_ineligible_n", 2024, "all")["value_numeric"],
        stat(conn, "registry.people_with_cf", 2024, "age_ge_60")["value_numeric"],
        stat(conn, "registry.modulator_ineligible_with_data_n", 2024, "age_ge_12_no_lung_transplant")[
            "value_numeric"
        ],
        stat(conn, "registry.cirrhosis_n", 2024, "cirrhosis")["value_numeric"],
        stat(conn, "registry.eligible_not_prescribed_n", 2024, "age_ge_12_in_2020")["value_numeric"],
        stat(conn, "registry.lung_transplants", 2024, "all")["value_numeric"],
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.barh(labels[::-1], list(reversed(values)), color=color)
    ax.set_title("Selected 2024 residual-population counts (not a single denominator)")
    _style_axes(ax, "", "People (count)")
    fig.text(
        0.01,
        -0.05,
        "FACT. Source: CFF 2024 ADR. Bars use different eligibility rules (full Registry vs complications vs 2020 eligibility cohort). Do not add them.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "residual_population_counts.png")

    pct_labels = [
        "Modulator eligible after VTD (~)",
        "PERT",
        "Dornase alfa ages ≥6",
        "Adult CFRD",
        "Adult anxiety",
        "Adult depression",
        "PA among cultured",
        "IV-treated PEx",
    ]
    pct_values = [
        stat(conn, "registry.modulator_eligible_pct", 2024, "all")["value_numeric"],
        stat(conn, "registry.pert_pct", 2024, "all")["value_numeric"],
        stat(conn, "registry.dornase_pct", 2024, "age_ge_6")["value_numeric"],
        stat(conn, "registry.cfrd_pct", 2024, "age_ge_18_no_lung_transplant")["value_numeric"],
        stat(conn, "registry.anxiety_pct", 2024, "age_ge_18_mental_health")["value_numeric"],
        stat(conn, "registry.depression_pct", 2024, "age_ge_18_mental_health")["value_numeric"],
        stat(conn, "registry.pseudomonas_pct", 2024, "cultured")["value_numeric"],
        stat(conn, "registry.pex_iv_pct", 2024, "all")["value_numeric"],
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.barh(pct_labels[::-1], list(reversed(pct_values)), color=color)
    ax.set_xlim(0, 100)
    ax.set_title("Selected 2024 residual-burden percentages (mixed denominators)")
    _style_axes(ax, "", "Percent")
    fig.text(
        0.01,
        -0.05,
        "FACT. Source: CFF 2024 ADR. Eligibility ~92% is approximate as published. CFRD/anxiety/depression use the complications or mental-health denominators, not 33,989.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "residual_burden_percents.png")

    return fig_dir


def run_landscape(db_path: Path | None = None) -> dict[str, str | int]:
    conn = connect(db_path)
    try:
        tables = build_tables(conn)
        trials = trial_frame(conn)
        out_tables = write_tables(tables)
        out_figs = write_figures(conn, trials)
    finally:
        conn.close()
    return {
        "tables_dir": str(out_tables),
        "figures_dir": str(out_figs),
        "claims": int(len(tables["landscape_claims"])),
        "ncfb_flagged": int(len(tables["ncfb_flagged_trials"])),
        "solved_unsolved_rows": int(len(tables["solved_unsolved"])),
    }
