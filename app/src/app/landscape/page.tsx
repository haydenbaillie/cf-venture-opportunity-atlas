import Note from "@/components/Note";
import PageNav from "@/components/PageNav";
import snapshot from "@/data/snapshot.json";
import { NEED_LABELS } from "@/lib/labels";
import { claim, fmt } from "@/lib/snapshot";

export default function LandscapePage() {
  const people = claim("C001");
  const ineligible = claim("C005");
  const notRx = claim("C007");
  const pex = claim("C010");
  const pa = claim("C012");
  const cfrd = claim("C014");
  const pert = claim("C015");

  return (
    <div className="space-y-10">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">Patient landscape</p>
        <h1 className="font-serif text-4xl">What has been solved. What remains.</h1>
        <p className="max-w-2xl text-muted">
          Published facts from the US Cystic Fibrosis Foundation Patient Registry
          2024. This page is the leftover-disease picture. It is not a ranking and
          not a map of companies.
        </p>
      </header>

      <Note title="Do not add these leftovers">
        <p>
          Each number comes from a different table, so they are not slices of the
          same pie. People who cannot take a modulator are not the same group as
          people with CF-related diabetes, who are not the same group as people
          who still grow Pseudomonas. Adding them invents a market that does not
          exist. 33,989 is a headcount, not a commercial market size.
        </p>
      </Note>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Fact k="People in the Registry" v={fmt(people.value_numeric)} note="US care-center headcount, not a market size" />
        <Fact
          k="Cannot take a modulator"
          v={fmt(ineligible.value_numeric)}
          note="Ineligible by age or gene type. Many are too young. Use 1,226 for adolescents/adults with data."
        />
        <Fact
          k="Could take one, did not"
          v={fmt(notRx.value_numeric)}
          note="Eligible in 2020, no modulator prescription 2022–24. Mixed reasons — not the same as the 2,434."
        />
        <Fact k="Adults with CF-related diabetes" v="29.3%" note="CFRD in adults. Do not apply this percent to 33,989." />
        <Fact k="IV-treated lung flares" v={`${pex.value_numeric}%`} note="Pulmonary exacerbations. Was 35.8% in 2009." />
        <Fact k="Pseudomonas in cultured patients" v={`${pa.value_numeric}%`} note="PA among people who had a culture. Was 52.0% in 2009." />
        <Fact k="Still using pancreatic enzymes" v={`${pert.value_numeric}%`} note="PERT is a solved product class, not leftover CFTR." />
        <Fact
          k="CFRD, complications table"
          v={`${cfrd.value_numeric}%`}
          note="Same diabetes, different slice (~32,492 people, not 33,989)."
        />
      </section>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl">Solved vs leftover, by topic</h2>
        <p className="max-w-2xl text-sm text-muted">
          Solved means a class that already works for most people. Remains is a
          countable leftover. Interpretation is what we think that means — still
          not a score.
        </p>
        {snapshot.solved_unsolved.map((row) => (
          <article key={row.domain} className="border border-mist bg-white p-5">
            <h3 className="font-serif text-xl">{row.domain}</h3>
            <p className="mt-1 text-xs uppercase tracking-wide text-muted">
              {needLine(row.need_id)}
            </p>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <Block title="Solved" text={row.solved_fact} />
              <Block title="Still leftover" text={row.remains_fact} />
              <Block title="What we think it means" text={row.interpretation} />
            </div>
          </article>
        ))}
      </section>

      <PageNav current="/landscape" />
    </div>
  );
}

function needLine(needId: string | null) {
  if (!needId) return "Not a patient leftover — this card hands off to Pipeline and Map";
  return needId
    .split(";")
    .map((id) => (NEED_LABELS[id] ? `${id} · ${NEED_LABELS[id]}` : id))
    .join(" · ");
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

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-muted">{text}</p>
    </div>
  );
}
