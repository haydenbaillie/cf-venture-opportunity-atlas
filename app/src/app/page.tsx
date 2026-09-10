import Link from "next/link";
import snapshot from "@/data/snapshot.json";
import { claim, fmt } from "@/lib/snapshot";

export default function HomePage() {
  const people = claim("C001");
  const survival = claim("C002");
  const eligible = claim("C004");
  const top = [...snapshot.need_scores].sort((a, b) => a.rank_default - b.rank_default)[0];

  return (
    <div className="space-y-10">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">Healthcare venture research · snapshot</p>
      <h1 className="max-w-3xl font-serif text-4xl leading-tight md:text-5xl">
        Where unmet need remains in cystic fibrosis after highly effective modulators.
      </h1>
      <p className="max-w-2xl text-lg text-muted">
        {snapshot.meta.disclaimer} Data as of the CFF 2024 Patient Registry and a
        ClinicalTrials.gov interventional pull retrieved 9 Sep 2026.
      </p>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="People in the 2024 US Registry" value={fmt(people.value_numeric)} />
        <Stat label="Predicted median survival" value={`${survival.value_numeric} yrs`} note="38.0 in 2009" />
        <Stat label="Modulator-eligible after Alyftrek" value="~92%" />
        <Stat
          label={`${top.need_id} default opportunity index`}
          value={`${top.display_default}/100`}
          note={top.evidence_confidence}
        />
      </section>
      <p className="text-xs text-muted">
        FACT. Registry source: {snapshot.meta.registry_source}. Eligibility ~92% is
        approximate as published. The index is a hypothesis, not a funding signal.
      </p>

      <section className="border border-mist bg-white p-6">
        <h2 className="font-serif text-2xl">The question</h2>
        <p className="mt-3 max-w-3xl text-muted">
          Where do meaningful unmet needs remain, how well is the current therapeutic
          and clinical-development ecosystem addressing them, and which areas appear
          most promising for future innovation or company formation?
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <ReadCard
          title="FACT"
          body="A published CFF number or a retrieved ClinicalTrials.gov count, with a source and date."
        />
        <ReadCard
          title="ANALYSIS"
          body="A filter or join we computed, including the NCFB heuristic and the reviewed competitive map."
        />
        <ReadCard
          title="HYPOTHESIS"
          body="An opportunity score or thesis. Always shown with 1–5 components, evidence confidence, and kill criteria."
        />
      </section>

      <section>
        <h2 className="font-serif text-2xl">Start here</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <StartLink href="/landscape" title="Landscape" body="What has been solved. What remains countable." />
          <StartLink href="/map" title="Competitive map" body="Reviewed CF programs only. NCFB stays off." />
          <StartLink href="/opportunities" title="Opportunities" body="Ranked needs, weight presets, and seven challenge memos." />
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="border border-mist bg-white p-4">
      <div className="font-serif text-3xl text-accent">{value}</div>
      <div className="mt-2 text-sm">{label}</div>
      {note ? <div className="mt-1 text-xs text-muted">{note}</div> : null}
    </div>
  );
}

function ReadCard({ title, body }: { title: string; body: string }) {
  return (
    <div className="border border-mist p-5">
      <h3 className="text-sm font-semibold uppercase tracking-wide">{title}</h3>
      <p className="mt-2 text-sm text-muted">{body}</p>
    </div>
  );
}

function StartLink({ href, title, body }: { href: string; title: string; body: string }) {
  return (
    <Link href={href} className="block border border-mist bg-white p-5 no-underline hover:border-accent">
      <div className="font-serif text-xl text-ink">{title}</div>
      <p className="mt-2 text-sm text-muted">{body}</p>
    </Link>
  );
}
