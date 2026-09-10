import snapshot from "@/data/snapshot.json";
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
          US CFF Patient Registry 2024. Do not add residual counts; they use different
          denominators. This is FACT unless labeled otherwise.
        </p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Fact k="Registry" v={fmt(people.value_numeric)} />
        <Fact k="Ineligible by age or genotype" v={fmt(ineligible.value_numeric)} />
        <Fact k="Eligible 2020, no Rx 2022–24" v={fmt(notRx.value_numeric)} />
        <Fact k="Adult CFRD" v="29.3%" />
        <Fact k="IV-treated PEx" v={`${pex.value_numeric}%`} />
        <Fact k="PA among cultured" v={`${pa.value_numeric}%`} />
        <Fact k="PERT" v={`${pert.value_numeric}%`} />
        <Fact k="CFRD, complications pop." v={`${cfrd.value_numeric}%`} />
      </section>

      <section className="space-y-4">
        {snapshot.solved_unsolved.map((row) => (
          <article key={row.domain} className="border border-mist bg-white p-5">
            <div className="text-xs uppercase tracking-wide text-muted">
              {row.need_id || "Pipeline"} · {row.domain}
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <Block title="Solved" text={row.solved_fact} />
              <Block title="Remains" text={row.remains_fact} />
              <Block title="Interpretation" text={row.interpretation} />
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

function Fact({ k, v }: { k: string; v: string }) {
  return (
    <div className="border border-mist bg-white p-4">
      <div className="font-serif text-2xl text-accent">{v}</div>
      <div className="mt-1 text-sm text-muted">{k}</div>
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
