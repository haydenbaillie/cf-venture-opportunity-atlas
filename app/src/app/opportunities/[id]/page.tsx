import Link from "next/link";
import { notFound } from "next/navigation";
import snapshot from "@/data/snapshot.json";
import { STANCE_LABELS } from "@/lib/labels";

type PageProps = { params: Promise<{ id: string }> };

export function generateStaticParams() {
  return snapshot.theses.map((row) => ({ id: row.thesis_id }));
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const thesis = snapshot.theses.find((row) => row.thesis_id === id);
  if (!thesis) return { title: "Thesis" };
  return { title: `${thesis.thesis_id} · ${thesis.title}` };
}

export default async function ThesisMemoPage({ params }: PageProps) {
  const { id } = await params;
  const thesis = snapshot.theses.find((row) => row.thesis_id === id);
  if (!thesis) notFound();

  const stance = STANCE_LABELS[thesis.formation_stance] || thesis.formation_stance;
  const score = Number(thesis.parent_need_score ?? thesis.display_default);
  const others = snapshot.theses.filter((row) => row.thesis_id !== thesis.thesis_id);

  return (
    <div className="space-y-10">
      <p className="text-sm">
        <Link href="/opportunities" className="text-muted no-underline hover:text-ink">
          ← Opportunities
        </Link>
      </p>
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">
          {stance} · {thesis.need_id}
        </p>
        <h1 className="font-serif text-4xl">
          {thesis.thesis_id} · {thesis.title}
        </h1>
        <p className="text-sm">
          Opportunity Score: {score}/100 · Evidence: {thesis.evidence_confidence}
        </p>
        <p className="max-w-2xl text-muted">{thesis.headline}</p>
      </header>

      <p className="max-w-2xl text-xs text-muted">{snapshot.meta.disclaimer}</p>

      <Layer k="HYPOTHESIS" body={thesis.one_liner} />
      <Layer k="FACT" body={thesis.fact} />
      <Layer k="ANALYSIS" body={thesis.analysis} />
      <Layer k="INTERPRETATION" body={thesis.interpretation} />

      <section className="grid gap-4 md:grid-cols-2">
        <Case title="Bull case" body={thesis.bull_case} />
        <Case title="Bear case" body={thesis.bear_case} tone="gold" />
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Counterarguments</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          {thesis.counterarguments.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">What would have to be true</h2>
        <p className="text-sm text-muted">{thesis.what_would_have_to_be_true}</p>
      </section>

      <section className="border border-gold/40 bg-white p-5">
        <h2 className="font-serif text-2xl">Kill criteria</h2>
        <p className="mt-3 text-sm">{thesis.kill_criteria}</p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Remaining diligence</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          {thesis.remaining_diligence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="border border-mist bg-white p-5">
        <h2 className="font-serif text-2xl">Verdict</h2>
        <p className="mt-3 text-sm">{thesis.verdict}</p>
        <p className="mt-3 text-xs text-muted">
          This card inherits the parent need score. It is not a second ranking and
          not a funding recommendation.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Other memos</h2>
        <div className="flex flex-wrap gap-3 text-sm">
          {others.map((row) => (
            <Link key={row.thesis_id} href={`/opportunities/${row.thesis_id}`}>
              {row.thesis_id}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function Layer({ k, body }: { k: string; body: string }) {
  return (
    <section className="space-y-2">
      <h2 className="text-sm font-semibold uppercase tracking-wide">{k}</h2>
      <p className="max-w-3xl text-sm text-muted">{body}</p>
    </section>
  );
}

function Case({ title, body, tone }: { title: string; body: string; tone?: "gold" }) {
  return (
    <article className={`border p-5 ${tone === "gold" ? "border-gold/40 bg-white" : "border-mist bg-white"}`}>
      <h2 className="font-serif text-2xl">{title}</h2>
      <p className="mt-3 text-sm text-muted">{body}</p>
    </article>
  );
}
