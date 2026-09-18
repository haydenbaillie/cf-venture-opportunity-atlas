import Note from "@/components/Note";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { fmtDate, summary } from "@/lib/snapshot";

export default function PipelinePage() {
  const years = snapshot.trials_by_year.filter(
    (row) => row.start_year && Number(row.start_year) >= 2008 && Number(row.start_year) <= 2026,
  );
  const max = Math.max(...years.map((row) => Number(row.n_all) || 0), 1);
  const reviewed = summary("trials_reviewed");
  const ncfb = summary("ncfb_heuristic_flagged");
  const mapAssets = summary("map_assets");

  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Clinical development</p>
        <h1 className="font-serif text-4xl">The raw CF-tagged extract is not the pipeline.</h1>
        <p className="max-w-2xl text-muted">
          ClinicalTrials.gov is a public list of studies. Searching “cystic fibrosis”
          also pulls in a different lung disease and other noise. Rankings on this
          site never use that unfiltered list.
        </p>
      </header>

      <Note title="What this page is">
        <p>
          ANALYSIS, not a score. The download is from ClinicalTrials.gov, retrieved{" "}
          {fmtDate(snapshot.meta.trials_retrieved_at)}. Teal bars below are
          CF-like. Gray bars are likely non-CF bronchiectasis (NCFB) tagging noise.
          2026 is a partial year because the pull was 9 September.
        </p>
      </Note>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Fact
          k="Studies tagged cystic fibrosis"
          v="1,209"
          note="The messy search result. Do not rank from this."
        />
        <Fact
          k="Likely a different lung disease"
          v={String(ncfb.value_numeric)}
          note="NCFB heuristic: a title/summary guess, not a diagnosis."
        />
        <Fact
          k="Looked at by a person"
          v={String(reviewed.value_numeric)}
          note="Only these trial records received a manual CF vs not overlay."
        />
        <Fact
          k="Programs on the next page"
          v={String(mapAssets.value_numeric)}
          note="Reviewed CF assets. Grain is program, not trial listing."
        />
      </section>

      <section>
        <h2 className="font-serif text-2xl">When studies started</h2>
        <p className="mt-2 text-sm text-muted">
          Each row is a year. The number on the right is the total. Starts peaked
          around 2015. The last bar is not “the field died” — 2026 is incomplete.
        </p>
        <div className="mt-6 space-y-1">
          {years.map((row) => {
            const all = Number(row.n_all) || 0;
            const ncfbN = Number(row.n_likely_ncfb) || 0;
            const cf = Number(row.n_cf_like) || 0;
            return (
              <div key={row.start_year} className="grid grid-cols-[3.5rem_1fr_2.5rem] items-center gap-3 text-xs">
                <div className="text-muted">{row.start_year}</div>
                <div className="flex h-3 overflow-hidden bg-mist">
                  <div className="h-full bg-accent" style={{ width: `${(cf / max) * 100}%` }} />
                  <div className="h-full bg-[#8a9aa3]" style={{ width: `${(ncfbN / max) * 100}%` }} />
                </div>
                <div className="text-right text-muted">{all}</div>
              </div>
            );
          })}
        </div>
        <p className="mt-3 text-xs text-muted">Teal: CF-like. Gray: likely NCFB noise.</p>
      </section>

      <section className="border border-mist bg-white p-5 text-sm text-muted">
        Of 13 recruiting flagged records in the Phase 3 extract, 9 were industry-sponsored.
        Raw “industry recruiting in CF” is inflated by non-CF bronchiectasis programs.
        NCT01851694 (incretin hormones in CF) was a heuristic false positive and is labeled
        CF; it is not a product on the map.
      </section>

      <PageNav current="/pipeline" />
    </div>
  );
}

function Fact({ k, v, note }: { k: string; v: string; note?: string }) {
  return (
    <div className="border border-mist bg-white p-4">
      <div className="font-serif text-2xl text-accent">{v}</div>
      <div className="mt-1 text-sm">{k}</div>
      {note ? <div className="mt-1 text-xs text-muted">{note}</div> : null}
    </div>
  );
}
