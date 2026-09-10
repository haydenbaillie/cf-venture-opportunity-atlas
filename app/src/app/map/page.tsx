"use client";

import { useMemo, useState } from "react";
import snapshot from "@/data/snapshot.json";
import { STAGE_LABELS, STAGES, STRATEGY_LABELS } from "@/lib/labels";

export default function MapPage() {
  const [strategy, setStrategy] = useState("all");
  const [need, setNeed] = useState("all");

  const strategies = useMemo(
    () => Array.from(new Set(snapshot.competitive_map.map((row) => row.strategy))).sort(),
    [],
  );

  const counts = useMemo(() => {
    const lookup = new Map<string, number>();
    for (const row of snapshot.competitive_map) {
      lookup.set(`${row.strategy}|${row.stage}`, row.n_assets);
    }
    return lookup;
  }, []);

  const assets = snapshot.map_assets.filter((row) => {
    if (strategy !== "all" && row.strategy !== strategy) return false;
    if (need !== "all" && !(row.need_ids || "").includes(need)) return false;
    return true;
  });

  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Reviewed competitive map</p>
        <h1 className="font-serif text-4xl">Every row here has been reviewed as CF.</h1>
        <p className="max-w-2xl text-muted">
          ANALYSIS. Map grain is program/asset, crowding_unit=1 for the grid.
          Unreviewed trials never enter this page. NCFB programs are excluded.
        </p>
      </header>

      <section className="overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse text-center text-xs">
          <thead>
            <tr>
              <th className="border border-mist bg-white p-2 text-left">Strategy</th>
              {STAGES.map((stage) => (
                <th key={stage} className="border border-mist bg-white p-2">
                  {STAGE_LABELS[stage]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {strategies.map((item) => (
              <tr key={item}>
                <td className="border border-mist bg-white p-2 text-left">
                  {STRATEGY_LABELS[item] || item}
                </td>
                {STAGES.map((stage) => {
                  const n = counts.get(`${item}|${stage}`) || 0;
                  return (
                    <td
                      key={stage}
                      className="border border-mist p-2"
                      style={{ background: n ? `rgba(31,78,95,${Math.min(0.15 + n * 0.12, 0.7)})` : "white" }}
                    >
                      {n || ""}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="flex flex-wrap gap-4 text-sm">
        <label className="flex items-center gap-2">
          Strategy
          <select
            className="border border-mist bg-white px-2 py-1"
            value={strategy}
            onChange={(event) => setStrategy(event.target.value)}
          >
            <option value="all">All</option>
            {strategies.map((item) => (
              <option key={item} value={item}>
                {STRATEGY_LABELS[item] || item}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          Need
          <select
            className="border border-mist bg-white px-2 py-1"
            value={need}
            onChange={(event) => setNeed(event.target.value)}
          >
            <option value="all">All</option>
            {["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"].map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </label>
        <p className="text-muted">{assets.length} assets</p>
      </section>

      <section className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className="bg-white">
              {["Asset", "Company", "Strategy", "Need", "Stage", "Whitespace"].map((h) => (
                <th key={h} className="border border-mist p-2 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {assets.map((row) => (
              <tr key={row.asset_id}>
                <td className="border border-mist p-2">{row.asset_name}</td>
                <td className="border border-mist p-2 text-muted">{row.company_name || "—"}</td>
                <td className="border border-mist p-2">{STRATEGY_LABELS[row.strategy] || row.strategy}</td>
                <td className="border border-mist p-2">{row.need_ids}</td>
                <td className="border border-mist p-2">{STAGE_LABELS[row.stage] || row.stage}</td>
                <td className="border border-mist p-2">{row.whitespace_relevant ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
