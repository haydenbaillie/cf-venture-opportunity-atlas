import Link from "next/link";
import { PAGES, type PageHref } from "@/lib/pages";

type Neighbor = { href: string; label: string; hint: string };

export default function PageNav({
  current,
  prev,
  next,
}: {
  current?: PageHref;
  prev?: Neighbor | null;
  next?: Neighbor | null;
}) {
  const index = current ? PAGES.findIndex((page) => page.href === current) : -1;
  const resolvedPrev = prev !== undefined ? prev : index > 0 ? PAGES[index - 1] : null;
  const resolvedNext =
    next !== undefined ? next : index >= 0 && index < PAGES.length - 1 ? PAGES[index + 1] : null;
  const step = index >= 0 ? index + 1 : null;

  return (
    <nav className="border-t border-mist pt-8" aria-label="Continue reading">
      {step ? (
        <p className="mb-4 text-xs uppercase tracking-[0.18em] text-muted">
          Step {step} of {PAGES.length}
        </p>
      ) : (
        <p className="mb-4 text-xs uppercase tracking-[0.18em] text-muted">Continue</p>
      )}
      <div className="grid gap-3 sm:grid-cols-2">
        {resolvedPrev ? (
          <Link
            href={resolvedPrev.href}
            className="block border border-mist bg-white p-4 no-underline hover:border-accent"
          >
            <div className="text-xs uppercase tracking-wide text-muted">Previous</div>
            <div className="mt-1 font-serif text-xl text-ink">{resolvedPrev.label}</div>
            <p className="mt-1 text-sm text-muted">{resolvedPrev.hint}</p>
          </Link>
        ) : (
          <div className="hidden sm:block" />
        )}
        {resolvedNext ? (
          <Link
            href={resolvedNext.href}
            className="block border border-accent bg-accent p-4 text-white no-underline hover:opacity-90"
          >
            <div className="text-xs uppercase tracking-wide text-white/80">Next</div>
            <div className="mt-1 font-serif text-xl">{resolvedNext.label}</div>
            <p className="mt-1 text-sm text-white/85">{resolvedNext.hint}</p>
          </Link>
        ) : null}
      </div>
    </nav>
  );
}
