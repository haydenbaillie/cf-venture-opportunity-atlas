"use client";

import { useMemo, useState } from "react";
import ButtonLink from "@/components/ButtonLink";
import Note from "@/components/Note";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { NEED_LABELS, STANCE_HELP, STANCE_LABELS } from "@/lib/labels";
import {
  COMPONENT_HELP,
  COMPONENT_LABELS,
  COMPONENTS,
  PRESET_HELP,
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
          Each leftover problem gets six 1–5 scores. Those scores are mixed with
          weights you can change. The result is a number from 20 to 100. It is a
          hypothesis, not a funding recommendation. Evidence (High / Moderate / Low)
          sits beside the number and is never mixed into it.
        </p>
      </header>

      <Note title="How to read this page">
        <p>
          Start with the ranking table, not the first thesis card. On default
          weights, N5 (CF-related diabetes) is 77 and N1 (restoration) is 72. Diabetes
          wins because restoration is crowded with companies, not because diabetes is
          a bigger CFTR hole. Click Patient impact to see restoration move first, then
          click Default again so the memos match the written ranking.
        </p>
      </Note>

      <section className="space-y-3">
        <div className="flex flex-wrap gap-2">
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
        </div>
        <p className="text-sm text-muted">{PRESET_HELP[preset]}</p>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        {COMPONENTS.map((id) => (
          <label key={id} className="grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
            <span>
              {COMPONENT_LABELS[id]}{" "}
              <span className="text-muted">{Math.round(weights[id] * 100)}%</span>
              <span className="mt-0.5 block text-xs text-muted">{COMPONENT_HELP[id]}</span>
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
      <p className="text-xs text-muted">
        Moving a slider switches you to Custom and renormalizes so the six weights
        still add to 100%. The 1–5 scores themselves do not change — only how much
        each one matters.
      </p>

      <section className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className="bg-white">
              {["Rank", "Leftover problem", "Score /100", "Evidence", "Patient need", "Treatment gap", "White space"].map(
                (h) => (
                  <th key={h} className="border border-mist p-2 font-medium">
                    {h}
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody>
            {ranked.map((row, index) => (
              <tr key={row.need_id}>
                <td className="border border-mist p-2">{index + 1}</td>
                <td className="border border-mist p-2">
                  <div>
                    {row.need_id} · {NEED_LABELS[row.need_id] || row.subcategory}
                  </div>
                  <div className="text-xs text-muted">{row.subcategory}</div>
                </td>
                <td className="border border-mist p-2 font-medium">{row.live}/100</td>
                <td className="border border-mist p-2">{row.evidence_confidence}</td>
                <td className="border border-mist p-2">{row.patient_need}</td>
                <td className="border border-mist p-2">{row.treatment_gap}</td>
                <td className="border border-mist p-2">{row.competitive_whitespace}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <p className="text-xs text-muted">
        Patient need, treatment gap, and white space are three of the six 1–5
        components. The live score uses all six plus the weights above.
      </p>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl">Theses with kill criteria</h2>
        <p className="text-sm text-muted">
          A thesis is a specific bet hanging off a leftover problem. It inherits
          that problem’s score — this is not a second ranking. Live numbers on these
          cards follow the weights above. The written memos use the default score.
          No thesis is only a bull case.
        </p>
        {snapshot.theses.map((thesis) => {
          const live = scoreByNeed[thesis.need_id];
          const stance = STANCE_LABELS[thesis.formation_stance] || thesis.formation_stance;
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
                {stance} · {thesis.need_id} · {NEED_LABELS[thesis.need_id] || thesis.need_id}
              </p>
              <p className="mt-1 text-xs text-muted">
                {STANCE_HELP[thesis.formation_stance] || ""}
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
                <ButtonLink href={`/opportunities/${thesis.thesis_id}`}>
                  Open the full memo
                </ButtonLink>
              </p>
            </article>
          );
        })}
      </section>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl">Scored, but not treated as a new company</h2>
        <p className="text-sm text-muted">
          These two leftovers stayed in the ranking so the set is honest. They do
          not get a company-formation card, because a score is not a reason to
          incorporate.
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

      <PageNav current="/opportunities" />
    </div>
  );
}
