import Link from "next/link";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { LAYER_HELP, NEED_LABELS } from "@/lib/labels";
import { claim, fmt } from "@/lib/snapshot";

export default function HomePage() {
  const people = claim("C001");
  const survival = claim("C002");
  const top = [...snapshot.need_scores].sort((a, b) => a.rank_default - b.rank_default)[0];
  const topName = NEED_LABELS[top.need_id] || top.need_id;

  return (
    <div className="space-y-10">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">
        Healthcare venture research · snapshot
      </p>
      <h1 className="max-w-3xl font-serif text-4xl leading-tight md:text-5xl">
        Where unmet need remains in cystic fibrosis after highly effective modulators.
      </h1>
      <p className="max-w-2xl text-lg text-muted">
        This is a public-data research memo with a website on top. It is not a
        company pitch, not medical advice, and not a recommendation to buy or sell
        anything. Data as of the Cystic Fibrosis Foundation 2024 Patient Registry
        and a ClinicalTrials.gov download from 9 Sep 2026.
      </p>
      <p className="max-w-2xl text-muted">
        Cystic fibrosis is a genetic disease. For most people with the right gene
        changes, a class of pills called CFTR modulators (Trikafta, and later
        Alyftrek) changed survival. This project asks what is still unsolved, where
        companies are already working, and which leftovers are worth a closer look.
      </p>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="People in the 2024 US Registry"
          value={fmt(people.value_numeric)}
          note="A US care-center headcount, not a market size"
        />
        <Stat
          label="Predicted median survival"
          value={`${survival.value_numeric} yrs`}
          note="38.0 years in 2009. The typical patient is now an adult."
        />
        <Stat
          label="Eligible for a modulator after Alyftrek"
          value="~92%"
          note="Approximate as CFF published it. Eligible is not the same as taking one."
        />
        <Stat
          label={`Highest leftover score (${top.need_id})`}
          value={`${top.display_default}/100`}
          note={`${topName}. ${top.evidence_confidence} evidence — a hypothesis, not a funding signal.`}
        />
      </section>
      <p className="text-xs text-muted">
        The first three numbers are published facts. The 77 is a score this project
        computed. Registry source: {snapshot.meta.registry_source}.
      </p>

      <section className="border border-mist bg-white p-6">
        <h2 className="font-serif text-2xl">The question</h2>
        <p className="mt-3 max-w-3xl text-muted">
          Where do meaningful unmet needs remain, how well is the current therapeutic
          and clinical-development ecosystem addressing them, and which areas appear
          most promising for future innovation or company formation?
        </p>
        <p className="mt-3 max-w-3xl text-sm text-muted">
          The pages follow that order: Landscape shows leftover disease, Map shows
          which leftovers already have companies, and Opportunities ranks the gaps
          and attaches a thesis you can kill.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <ReadCard title="FACT" body={LAYER_HELP.FACT} />
        <ReadCard title="ANALYSIS" body={LAYER_HELP.ANALYSIS} />
        <ReadCard title="HYPOTHESIS" body={LAYER_HELP.HYPOTHESIS} />
      </section>

      <details className="border border-mist bg-white p-5">
        <summary className="cursor-pointer font-serif text-xl">Words used on this site</summary>
        <dl className="mt-4 grid gap-4 text-sm md:grid-cols-2">
          <Term
            name="Modulator / HEMT"
            def="Pills that help some broken CFTR proteins work. Highly effective modulator therapy usually means Trikafta and now Alyftrek."
          />
          <Term
            name="CFF Registry"
            def="Yearly US report from accredited cystic fibrosis care centers. It covers people who consented, not every person with CF on earth."
          />
          <Term
            name="TAM"
            def="Total addressable market — a commercial sizing number. 33,989 is a headcount, not a TAM."
          />
          <Term
            name="Crowding / whitespace"
            def="Crowding means companies are already working on this problem. Whitespace means few or none. Empty is interesting. Empty is not proof a new company should exist."
          />
          <Term
            name="Need (N1–N8)"
            def="Eight leftover problem buckets this project scored. N5 is CF-related diabetes. N1 is mutation-agnostic CFTR restoration."
          />
          <Term
            name="Thesis (H1–H7)"
            def="A specific hypothesis hanging off a need. Each one has a bear case and kill criteria. The score is inherited from the parent need."
          />
          <Term
            name="Kill criteria"
            def="A pre-committed rule: if this happens, drop the idea. Without it, a score is just a cheerleading number."
          />
          <Term
            name="NCFB"
            def="Non-CF bronchiectasis — a different lung disease that shows up in a raw “cystic fibrosis” trial search. Those programs stay off the map."
          />
        </dl>
      </details>

      <section>
        <h2 className="font-serif text-2xl">Start here</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          You can jump, or use the Next button at the bottom of every page to read
          in order.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <StartLink
            href="/landscape"
            title="Landscape"
            body="What CFF published about patients — solved vs leftover."
          />
          <StartLink
            href="/map"
            title="Competitive map"
            body="Reviewed CF programs only. A different lung disease stays off."
          />
          <StartLink
            href="/opportunities"
            title="Opportunities"
            body="Ranked leftovers, sliders you can move, and seven challenge memos."
          />
        </div>
      </section>

      <PageNav current="/" />
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

function Term({ name, def }: { name: string; def: string }) {
  return (
    <div>
      <dt className="font-medium text-ink">{name}</dt>
      <dd className="mt-1 text-muted">{def}</dd>
    </div>
  );
}
