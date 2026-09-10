"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import snapshot from "@/data/snapshot.json";
import { STANCE_LABELS } from "@/lib/labels";
import {
  COMPONENT_LABELS,
  COMPONENTS,
  PRESET_LABELS,
  computeIndex,
  displayScore,
  normalizeWeights,
  weightsFromRows,
  type ComponentId,
  type Weights,
} from "@/lib/scoring";

const PRESETS = ["default", "patient_impact", "venture_creation", "commercial", "custom"] as const;

export default function OpportunitiesPage() {
  const defaultWeights = weightsFromRows(snapshot.weights, "default");
  const [preset, setPreset] = useState<(typeof PRESETS)[number]>("default");
  const [custom, setCustom] = useState<Weights>(defaultWeights);

  const weights = useMemo(() => {
    if (preset === "custom") return normalizeWeights(custom);
    return weightsFromRows(snapshot.weights, preset);
  }, [custom, preset]);

  const ranked = useMemo(() => {
    return snapshot.need_scores
      .map((need) => {
        const scores = Object.fromEntries(
          COMPONENTS.map((id) => [id, Number(need[id as ComponentId])]),
        ) as Record<ComponentId, number>;
        const value = computeIndex(scores, weights);
        return {
          ...need,
          live: displayScore(value),
          scores,
        };
      })
      .sort((a, b) => b.live - a.live || a.need_id.localeCompare(b.need_id));
  }, [weights]);

  const scoreByNeed = Object.fromEntries(ranked.map((row) => [row.need_id, row.live]));

  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Opportunity index</p>
        <h1 className="font-serif text-4xl">Exploratory scores, visible weights.</h1>
        <p className="max-w-2xl text-muted">
          HYPOTHESIS. Score = 20 × Σ(wᵢ × sᵢ). Evidence confidence is never folded
          into the number. Not a funding recommendation.
        </p>
      </header>

      <section className="flex flex-wrap gap-2">
        {PRESETS.map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => {
              setPreset(id);
              if (id !== "custom") setCustom(weightsFromRows(snapshot.weights, id));
            }}
            className={`border px-3 py-1 text-sm ${
              preset === id ? "border-accent bg-accent text-white" : "border-mist bg-white"
            }`}
          >
            {PRESET_LABELS[id]}
          </button>
        ))}
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {COMPONENTS.map((id) => (
          <label key={id} className="grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
            <span>
              {COMPONENT_LABELS[id]}{" "}
              <span className="text-muted">{Math.round(weights[id] * 100)}%</span>
            </span>
            <input
              type="range"
              min={0}
              max={40}
              value={Math.round(weights[id] * 100)}
              onChange={(event) => {
                setPreset("custom");
                setCustom({ ...weights, [id]: Number(event.target.value) / 100 });
              }}
            />
          </label>
        ))}
      </section>
      <p className="text-xs text-muted">Sliders renormalize to 100%. Component scores stay 1–5 as curated.</p>

      <section className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse text-left text-sm">
          <thead>
            <tr className="bg-white">
              {["Rank", "Need", "Score", "Evidence", "Need", "Gap", "Whitespace"].map((h) => (
                <th key={h} className="border border-mist p-2 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ranked.map((row, index) => (
              <tr key={row.need_id}>
                <td className="border border-mist p-2">{index + 1}</td>
                <td className="border border-mist p-2">
                  {row.need_id} {row.subcategory}
                </td>
                <td className="border border-mist p-2 font-medium">
                  {row.live}/100
                </td>
                <td className="border border-mist p-2">{row.evidence_confidence}</td>
                <td className="border border-mist p-2">{row.patient_need}</td>
                <td className="border border-mist p-2">{row.treatment_gap}</td>
                <td className="border border-mist p-2">{row.competitive_whitespace}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl">Theses with kill criteria</h2>
        <p className="text-sm text-muted">
          Live scores on these cards follow the weights above. Challenge memos use
          the default parent-need score. No thesis is only a bull case.
        </p>
        {snapshot.theses.map((thesis) => {
          const live = scoreByNeed[thesis.need_id];
          return (
            <article key={thesis.thesis_id} className="border border-mist bg-white p-5">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="font-serif text-xl">
                  {thesis.thesis_id} · {thesis.title}
                </h3>
                <p className="text-sm">
                  Opportunity Score: {live}/100 · Evidence: {thesis.evidence_confidence}
                </p>
              </div>
              <p className="mt-1 text-xs uppercase tracking-wide text-muted">
                {STANCE_LABELS[thesis.formation_stance] || thesis.formation_stance} · {thesis.need_id}
              </p>
              <p className="mt-3 text-sm">{thesis.one_liner}</p>
              <p className="mt-3 text-sm text-muted">
                <span className="font-medium text-ink">Would have to be true. </span>
                {thesis.what_would_have_to_be_true}
              </p>
              <p className="mt-2 text-sm text-muted">
                <span className="font-medium text-ink">Kill criteria. </span>
                {thesis.kill_criteria}
              </p>
              <p className="mt-4">
                <Link href={`/opportunities/${thesis.thesis_id}`} className="text-sm text-accent">
                  Open challenge memo
                </Link>
              </p>
            </article>
          );
        })}
      </section>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl">Scored, not default newcos</h2>
        <p className="text-sm text-muted">
          N2 and N7 stay in the investigation set. They do not get company-formation cards.
        </p>
        {snapshot.held_out.map((row) => (
          <article key={row.need_id} className="border border-mist p-5">
            <h3 className="font-serif text-xl">
              {row.need_id} · {row.title}
            </h3>
            <p className="mt-1 text-sm">
              Opportunity Score: {row.score_default}/100 · Evidence: Moderate
            </p>
            <p className="mt-3 text-sm text-muted">{row.why_held_out}</p>
            <p className="mt-3 text-sm font-medium">{row.verdict}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
