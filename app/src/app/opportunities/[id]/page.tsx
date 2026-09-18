import ButtonLink from "@/components/ButtonLink";
import Note from "@/components/Note";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { LAYER_HELP, NEED_LABELS, STANCE_HELP, STANCE_LABELS } from "@/lib/labels";
import { notFound } from "next/navigation";

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
  const index = snapshot.theses.findIndex((row) => row.thesis_id === thesis.thesis_id);
  const prevThesis = index > 0 ? snapshot.theses[index - 1] : null;
  const nextThesis = index < snapshot.theses.length - 1 ? snapshot.theses[index + 1] : null;
  const others = snapshot.theses.filter((row) => row.thesis_id !== thesis.thesis_id);

  return (
    <div className="space-y-10">
      <p className="text-sm">
        <ButtonLink href="/opportunities" tone="plain">
          ← All opportunities
        </ButtonLink>
      </p>
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">
          {stance} · {thesis.need_id} · {NEED_LABELS[thesis.need_id] || thesis.need_id}
        </p>
        <h1 className="font-serif text-4xl">
          {thesis.thesis_id} · {thesis.title}
        </h1>
        <p className="text-sm">
          Opportunity Score: {score}/100 · Evidence: {thesis.evidence_confidence}
        </p>
        <p className="max-w-2xl text-sm text-muted">
          {STANCE_HELP[thesis.formation_stance]} This card inherits the parent
          leftover’s score. It is not a second ranking.
        </p>
        <p className="max-w-2xl text-muted">{thesis.headline}</p>
      </header>

      <p className="max-w-2xl text-xs text-muted">{snapshot.meta.disclaimer}</p>

      <Note title="How to read this memo">
        <p>
          Fact is a published number. Analysis is what this project filtered or
          counted. Interpretation is what we think that means. Hypothesis is the
          bet. Then read the bear case and the kill box — those are the point.
        </p>
      </Note>

      <Layer k="HYPOTHESIS" body={thesis.one_liner} />
      <Layer k="FACT" body={thesis.fact} />
      <Layer k="ANALYSIS" body={thesis.analysis} />
      <Layer k="INTERPRETATION" body={thesis.interpretation} />

      <section className="grid gap-4 md:grid-cols-2">
        <Case
          title="Bull case"
          help="Why this leftover might be a real product question."
          body={thesis.bull_case}
        />
        <Case
          title="Bear case"
          help="Why it might already be solved, or never be a new company."
          body={thesis.bear_case}
          tone="gold"
        />
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">Counterarguments</h2>
        <p className="text-sm text-muted">Reasons a skeptical reader would push back.</p>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted">
          {thesis.counterarguments.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">What would have to be true</h2>
        <p className="text-sm text-muted">Assumptions the bet needs. If these fail, the thesis fails.</p>
        <p className="text-sm text-muted">{thesis.what_would_have_to_be_true}</p>
      </section>

      <section className="border border-gold/40 bg-white p-5">
        <h2 className="font-serif text-2xl">Kill the idea if</h2>
        <p className="mt-1 text-sm text-muted">
          A pre-committed rule. If this happens, drop the thesis rather than
          talking yourself into it.
        </p>
        <p className="mt-3 text-sm">{thesis.kill_criteria}</p>
      </section>

      <section className="space-y-3">
        <h2 className="font-serif text-2xl">What to check next</h2>
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
        <div className="flex flex-wrap gap-3">
          {others.map((row) => (
            <ButtonLink key={row.thesis_id} href={`/opportunities/${row.thesis_id}`} tone="plain">
              {row.thesis_id} · {row.title}
            </ButtonLink>
          ))}
        </div>
      </section>

      <PageNav
        prev={
          prevThesis
            ? {
                href: `/opportunities/${prevThesis.thesis_id}`,
                label: prevThesis.thesis_id,
                hint: prevThesis.title,
              }
            : { href: "/opportunities", label: "Opportunities", hint: "Ranked leftovers and all seven theses" }
        }
        next={
          nextThesis
            ? {
                href: `/opportunities/${nextThesis.thesis_id}`,
                label: nextThesis.thesis_id,
                hint: nextThesis.title,
              }
            : { href: "/methodology", label: "Methodology", hint: "Sources, scoring rules, and limits" }
        }
      />
    </div>
  );
}

function Layer({ k, body }: { k: string; body: string }) {
  return (
    <section className="space-y-2">
      <h2 className="text-sm font-semibold uppercase tracking-wide">{k}</h2>
      <p className="text-xs text-muted">{LAYER_HELP[k]}</p>
      <p className="max-w-3xl text-sm text-muted">{body}</p>
    </section>
  );
}

function Case({
  title,
  help,
  body,
  tone,
}: {
  title: string;
  help: string;
  body: string;
  tone?: "gold";
}) {
  return (
    <article className={`border p-5 ${tone === "gold" ? "border-gold/40 bg-white" : "border-mist bg-white"}`}>
      <h2 className="font-serif text-2xl">{title}</h2>
      <p className="mt-1 text-xs text-muted">{help}</p>
      <p className="mt-3 text-sm text-muted">{body}</p>
    </article>
  );
}
