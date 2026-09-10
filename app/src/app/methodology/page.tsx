import snapshot from "@/data/snapshot.json";

export default function MethodologyPage() {
  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Methods</p>
        <h1 className="font-serif text-4xl">Every major number has a source and a date.</h1>
        <p className="max-w-2xl text-muted">{snapshot.meta.disclaimer}</p>
      </header>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Sources</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          <li>
            {snapshot.meta.registry_source}. Public PDF; no patient-level API. US accredited
            care-center consenters.
          </li>
          <li>
            {snapshot.meta.trials_source}. Retrieved {snapshot.meta.trials_retrieved_at}. No API
            key. Sponsor-reported.
          </li>
          <li>
            CFF Drug Development Pipeline webpage, curated snapshot. No pipeline API.
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Classification</h2>
        <p className="text-sm text-muted">
          Keyword rules suggest a label for every trial. The competitive map and opportunity
          whitespace component use only review_status=reviewed, disease_area=cf, and
          map_eligible=1. The NCFB title/summary heuristic is a Phase 3 filter, not truth.
          NCT01851694 was overridden to CF and is not a map product.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Scoring</h2>
        <p className="text-sm text-muted">
          Score = 20 × Σ(wᵢ × sᵢ) with sᵢ on a 1–5 rubric. Default weights: patient need 25%,
          treatment gap 20%, competitive white space 20%, tractability 15%, economic 10%,
          why now 10%. Display as an integer /100 plus a separate High / Moderate / Low
          evidence label. Trial counts may inform whitespace after review; they do not set
          need, tractability, or why-now. Economic relevance is not a TAM.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Theses</h2>
        <p className="text-sm text-muted">
          Seven challenge memos inherit the parent need score. Each one has a bear
          case, counterarguments, remaining diligence, and kill criteria. N2 and N7
          stay scored and are not default company-formation cards.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Limitations</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          <li>Registry figures are US care-center consenters, not a global patient-level file.</li>
          <li>Complication prevalence generally excludes lung-transplant recipients.</li>
          <li>ClinicalTrials.gov misses most preclinical work and includes noisy condition tags.</li>
          <li>CFF pipeline listings include discontinued programs; Phase 4 review marks those off the map.</li>
          <li>The opportunity index is exploratory. It is not a valuation or a securities recommendation.</li>
        </ul>
      </section>
    </div>
  );
}
