import Note from "@/components/Note";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { fmtDate } from "@/lib/snapshot";

export default function MethodologyPage() {
  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Methods</p>
        <h1 className="font-serif text-4xl">Every major number has a source and a date.</h1>
        <p className="max-w-2xl text-muted">
          This page is the appendix. It does not change the ranking. It is here so
          a reader can see what was counted, what was filtered, and what public
          data cannot support.
        </p>
        <p className="max-w-2xl text-sm text-muted">{snapshot.meta.disclaimer}</p>
      </header>

      <Note title="In one sentence">
        <p>
          Patient numbers come from a public CFF PDF. Trial counts come from a
          dated ClinicalTrials.gov download. The map and the scores use only rows
          a person reviewed as cystic fibrosis. The 0–100 index is a weighted
          opinion with a separate evidence label, not a valuation.
        </p>
      </Note>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Sources</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          <li>
            {snapshot.meta.registry_source}. Public PDF; no patient-level API. US
            accredited care-center participants who consented.
          </li>
          <li>
            ClinicalTrials.gov interventional search for cystic fibrosis. Retrieved{" "}
            {fmtDate(snapshot.meta.trials_retrieved_at)}. No API key. Sponsors
            report their own studies.
          </li>
          <li>
            CFF Drug Development Pipeline webpage, curated snapshot. There is no
            pipeline API.
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">What gets onto the map</h2>
        <p className="text-sm text-muted">
          Keyword rules suggest a label for every trial. The competitive map and
          the “white space” part of the score use only rows marked reviewed, cystic
          fibrosis, and map-eligible. The NCFB title/summary rule is a first filter,
          not a diagnosis. NCT01851694 (a real CF diabetes study) was overridden to
          CF and is not a product on the map.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">How the 0–100 score is made</h2>
        <p className="text-sm text-muted">
          Each leftover problem gets six 1–5 scores: patient need, treatment gap,
          competitive white space, tractability, economic relevance, and why now.
          Default mix: 25%, 20%, 20%, 15%, 10%, 10%. Those are averaged with the
          weights, then multiplied by 20 so the index runs from 20 to 100. Evidence
          is a separate High / Moderate / Low label. Trial counts may inform white
          space after review; they do not set need, tractability, or why-now.
          Economic relevance is not a market-size overlay on 33,989 people.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Theses</h2>
        <p className="text-sm text-muted">
          Seven challenge memos inherit the parent leftover’s score. Each one has a
          bear case, counterarguments, remaining checks, and kill criteria. Eligible-but-not-prescribed
          (N2) and aging with CF (N7) stay scored and are not treated as default
          new companies.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">What this data cannot do</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          <li>Registry figures are US care-center consenters, not a global patient file.</li>
          <li>Complication percentages generally exclude lung-transplant recipients, which is why 19.2% is not 19.2% of 33,989.</li>
          <li>ClinicalTrials.gov misses most work that has not reached people, and condition tags are noisy.</li>
          <li>CFF pipeline listings include discontinued programs; review takes those off the map.</li>
          <li>The opportunity index is exploratory. It is not a valuation or a securities recommendation.</li>
        </ul>
      </section>

      <PageNav current="/methodology" />
    </div>
  );
}
