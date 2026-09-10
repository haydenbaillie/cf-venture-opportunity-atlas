"""Phase 5 opportunity scoring.

Component scores are curated 1-5 rubrics. Trial counts may inform competitive
white space only after Phase 4 review. Evidence confidence is never folded into
the 0-100 index.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from cf_atlas.paths import external_dir, processed_dir, repo_root
from cf_atlas.theses import run_theses

COMPONENTS = (
    "patient_need",
    "treatment_gap",
    "competitive_whitespace",
    "tractability",
    "economic",
    "why_now",
)

WHITESPACE_BAND_TO_ALLOWED = {
    "high": {1, 2},
    "moderate": {2, 3},
    "low": {3, 4},
    "none": {4, 5},
}

# N3 is scored 3 because of adjacent NCFB late-stage crowding, which the rubric
# treats as "several programs or late-stage crowding in an adjacent indication"
# even though CF-specific industry whitespace is none.
WHITESPACE_EXCEPTIONS = {"N3": {3}}


def load_weights(path: Path | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path or (external_dir() / "scoring_weights.csv"))
    totals = frame.groupby("preset_id")["weight"].sum()
    off = totals.loc[(totals - 1.0).abs() > 1e-9]
    if len(off):
        raise ValueError(f"Weights must sum to 1 per preset; got {off.to_dict()}")
    return frame


def load_component_scores(path: Path | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path or (external_dir() / "component_scores.csv"))
    scores = pd.to_numeric(frame["score"], errors="raise")
    if not ((scores == scores.round()) & scores.between(1, 5)).all():
        raise ValueError("Component scores must be integers 1-5.")
    frame = frame.copy()
    frame["score"] = scores.astype(int)
    needs = set(frame["need_id"])
    for need_id in needs:
        got = set(frame.loc[frame["need_id"] == need_id, "component_id"])
        missing = set(COMPONENTS) - got
        extra = got - set(COMPONENTS)
        if missing or extra:
            raise ValueError(f"{need_id} components missing={missing} extra={extra}")
    return frame


def compute_index(scores: dict[str, int], weights: dict[str, float]) -> float:
    return 20.0 * sum(weights[c] * scores[c] for c in COMPONENTS)


def display_score(value: float) -> int:
    return int(round(value))


def preset_weight_map(weights: pd.DataFrame, preset_id: str) -> dict[str, float]:
    subset = weights.loc[weights["preset_id"] == preset_id]
    if len(subset) != len(COMPONENTS):
        raise KeyError(f"Preset {preset_id} does not have six components")
    return {row.component_id: float(row.weight) for row in subset.itertuples(index=False)}


def need_score_table(component_scores: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    rows = []
    needs = sorted(component_scores["need_id"].unique())
    presets = list(weights["preset_id"].drop_duplicates())
    for need_id in needs:
        subset = component_scores.loc[component_scores["need_id"] == need_id]
        scores = {row.component_id: int(row.score) for row in subset.itertuples(index=False)}
        row: dict[str, object] = {"need_id": need_id}
        for component in COMPONENTS:
            row[component] = scores[component]
        for preset_id in presets:
            w = preset_weight_map(weights, preset_id)
            value = round(compute_index(scores, w), 10)
            row[f"score_{preset_id}"] = round(value, 2)
            row[f"display_{preset_id}"] = display_score(value)
        rows.append(row)
    out = pd.DataFrame(rows)
    out["rank_default"] = out["display_default"].rank(ascending=False, method="min").astype(int)
    return out.sort_values(["rank_default", "need_id"]).reset_index(drop=True)


def shift_weight(weights: dict[str, float], component: str, delta: float) -> dict[str, float]:
    shifted = dict(weights)
    shifted[component] = min(1.0, max(0.0, weights[component] + delta))
    remaining = 1.0 - shifted[component]
    others = [c for c in COMPONENTS if c != component]
    other_sum = sum(weights[c] for c in others)
    if other_sum <= 0:
        even = remaining / len(others)
        for c in others:
            shifted[c] = even
        return shifted
    for c in others:
        shifted[c] = remaining * (weights[c] / other_sum)
    return shifted


def sensitivity_table(component_scores: pd.DataFrame, weights: pd.DataFrame, delta: float = 0.10) -> pd.DataFrame:
    default = preset_weight_map(weights, "default")
    needs = sorted(component_scores["need_id"].unique())
    score_maps = {}
    for need_id in needs:
        subset = component_scores.loc[component_scores["need_id"] == need_id]
        score_maps[need_id] = {row.component_id: int(row.score) for row in subset.itertuples(index=False)}

    rows = []
    for component in COMPONENTS:
        for sign, label in ((-delta, "minus_10pp"), (delta, "plus_10pp")):
            w = shift_weight(default, component, sign)
            displays = {
                need_id: display_score(compute_index(score_maps[need_id], w)) for need_id in needs
            }
            ranked = sorted(displays.items(), key=lambda item: (-item[1], item[0]))
            for rank, (need_id, value) in enumerate(ranked, start=1):
                rows.append(
                    {
                        "shift_component": component,
                        "shift": label,
                        "need_id": need_id,
                        "display_score": value,
                        "rank": rank,
                        "weight_used": round(w[component], 4),
                    }
                )
    return pd.DataFrame(rows)


def rank_stability(need_scores: pd.DataFrame, sensitivity: pd.DataFrame) -> pd.DataFrame:
    default_top3 = set(need_scores.nsmallest(3, "rank_default")["need_id"])
    preset_ids = [
        p
        for p in ("default", "patient_impact", "venture_creation", "commercial")
        if f"display_{p}" in need_scores.columns
    ]
    rows = []
    for preset in preset_ids:
        col = f"display_{preset}"
        ranked = need_scores.sort_values([col, "need_id"], ascending=[False, True])
        top3 = set(ranked.head(3)["need_id"])
        rows.append(
            {
                "scenario": f"preset:{preset}",
                "top3": ";".join(ranked.head(3)["need_id"].tolist()),
                "top3_overlap_with_default": len(top3 & default_top3),
                "same_top3": int(top3 == default_top3),
            }
        )
    for component in COMPONENTS:
        for shift in ("minus_10pp", "plus_10pp"):
            subset = sensitivity.loc[
                (sensitivity["shift_component"] == component) & (sensitivity["shift"] == shift)
            ].sort_values(["rank", "need_id"])
            top3 = set(subset.head(3)["need_id"])
            rows.append(
                {
                    "scenario": f"{component}:{shift}",
                    "top3": ";".join(subset.head(3)["need_id"].tolist()),
                    "top3_overlap_with_default": len(top3 & default_top3),
                    "same_top3": int(top3 == default_top3),
                }
            )
    return pd.DataFrame(rows)


def attach_coverage(need_scores: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "need_id",
        "n_industry_whitespace",
        "crowding_band",
        "n_map_assets",
        "n_academic_map_assets",
        "n_auto_suggested_active_cf_like",
    ]
    merged = need_scores.merge(coverage[cols], on="need_id", how="left")
    if merged["crowding_band"].isna().any():
        missing = merged.loc[merged["crowding_band"].isna(), "need_id"].tolist()
        raise FileNotFoundError(
            f"Need coverage missing for {missing}. Run `python -m cf_atlas classify` first."
        )
    return merged


def validate_whitespace_alignment(need_scores: pd.DataFrame) -> None:
    for row in need_scores.itertuples(index=False):
        allowed = set(WHITESPACE_BAND_TO_ALLOWED[row.crowding_band])
        allowed |= WHITESPACE_EXCEPTIONS.get(row.need_id, set())
        if int(row.competitive_whitespace) not in allowed:
            raise ValueError(
                f"{row.need_id} whitespace score {row.competitive_whitespace} "
                f"incompatible with crowding_band={row.crowding_band}"
            )


def evidence_labels() -> dict[str, str]:
    return {
        "N1": "High",
        "N2": "Moderate",
        "N3": "Moderate",
        "N4": "Moderate",
        "N5": "Moderate",
        "N6": "Moderate",
        "N7": "Moderate",
        "N8": "Moderate",
    }


def join_theses(theses: pd.DataFrame, need_scores: pd.DataFrame) -> pd.DataFrame:
    keep = theses.merge(
        need_scores[
            [
                "need_id",
                "display_default",
                "rank_default",
                "display_patient_impact",
                "display_venture_creation",
                "display_commercial",
                "crowding_band",
                "n_industry_whitespace",
            ]
        ],
        on="need_id",
        how="left",
    )
    keep["evidence_confidence"] = keep["evidence_confidence"]
    keep["parent_need_score"] = keep["display_default"]
    keep["display_line"] = keep.apply(
        lambda r: f"Opportunity Score: {int(r.parent_need_score)}/100 · Evidence: {r.evidence_confidence}",
        axis=1,
    )
    return keep


def write_figures(need_scores: pd.DataFrame, destination: Path | None = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = destination or (repo_root() / "assets" / "figures")
    fig_dir.mkdir(parents=True, exist_ok=True)
    color = "#1f4e5f"
    tones = ["#1f4e5f", "#3d6b7a", "#8a9aa3", "#c4a35a"]

    def save(fig, name: str) -> None:
        fig.tight_layout()
        fig.savefig(fig_dir / name, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    ordered = need_scores.sort_values("rank_default")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.barh(ordered["need_id"][::-1], ordered["display_default"][::-1], color=color)
    ax.set_xlim(20, 100)
    ax.set_title("Opportunity index by unmet-need category (default weights)")
    ax.set_xlabel("Score /100")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.text(
        0.01,
        -0.06,
        "HYPOTHESIS index. 20 x sum(w_i s_i) with s_i on 1-5. Evidence confidence is not in the number. Not a funding recommendation.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "need_opportunity_scores.png")

    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    x = list(range(len(ordered)))
    width = 0.2
    presets = [
        ("display_default", "Default"),
        ("display_patient_impact", "Patient impact"),
        ("display_venture_creation", "Venture creation"),
        ("display_commercial", "Commercial"),
    ]
    for i, (col, label) in enumerate(presets):
        offset = (i - 1.5) * width
        ax.bar([p + offset for p in x], ordered[col], width=width, color=tones[i], label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(ordered["need_id"])
    ax.set_ylim(20, 100)
    ax.set_ylabel("Score /100")
    ax.set_title("Rank stability across weight presets")
    ax.legend(frameon=False, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.text(
        0.01,
        -0.06,
        "Same 1-5 components; weights in data/external/scoring_weights.csv. Phase 5 also shifts each default weight by +/-10 percentage points.",
        fontsize=8,
        color="#444444",
    )
    save(fig, "score_preset_comparison.png")
    return fig_dir


def run_score() -> dict[str, str | int]:
    coverage_path = processed_dir() / "classification" / "need_pipeline_coverage.csv"
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing {coverage_path}. Run `python -m cf_atlas classify` first.")
    coverage = pd.read_csv(coverage_path)
    weights = load_weights()
    components = load_component_scores()
    theses = pd.read_csv(external_dir() / "opportunity_theses.csv")
    needs = pd.read_csv(external_dir() / "unmet_needs.csv")

    scored = need_score_table(components, weights)
    scored = attach_coverage(scored, coverage)
    validate_whitespace_alignment(scored)
    labels = evidence_labels()
    scored["evidence_confidence"] = scored["need_id"].map(labels)
    scored["display_line"] = scored.apply(
        lambda r: f"Opportunity Score: {int(r.display_default)}/100 · Evidence: {r.evidence_confidence}",
        axis=1,
    )
    scored = scored.merge(needs[["need_id", "category", "subcategory"]], on="need_id", how="left")

    sensitivity = sensitivity_table(components, weights)
    stability = rank_stability(scored, sensitivity)
    thesis_out = join_theses(theses, scored)

    wide_components = components.pivot(index="need_id", columns="component_id", values="score").reset_index()
    detail = components.merge(
        scored[["need_id", "display_default", "rank_default", "evidence_confidence", "crowding_band"]],
        on="need_id",
        how="left",
    )

    out_dir = processed_dir() / "scoring"
    out_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out_dir / "need_scores.csv", index=False)
    detail.to_csv(out_dir / "component_detail.csv", index=False)
    wide_components.to_csv(out_dir / "component_matrix.csv", index=False)
    sensitivity.to_csv(out_dir / "sensitivity.csv", index=False)
    stability.to_csv(out_dir / "rank_stability.csv", index=False)
    thesis_out.to_csv(out_dir / "theses.csv", index=False)
    memo_result = run_theses(thesis_out)
    figs = write_figures(scored)
    top = scored.iloc[0]
    return {
        "tables_dir": str(out_dir),
        "figures_dir": str(figs),
        "needs_scored": int(len(scored)),
        "theses": int(len(thesis_out)),
        "memo_docs": memo_result["docs_dir"],
        "top_need": str(top["need_id"]),
        "top_score": int(top["display_default"]),
        "stable_top3_scenarios": int(stability["same_top3"].sum()),
        "scenarios": int(len(stability)),
    }
