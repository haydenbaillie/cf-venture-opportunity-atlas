import Link from "next/link";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/landscape", label: "Landscape" },
  { href: "/pipeline", label: "Pipeline" },
  { href: "/map", label: "Map" },
  { href: "/opportunities", label: "Opportunities" },
  { href: "/methodology", label: "Methodology" },
];

export default function Nav() {
  return (
    <header className="border-b border-mist bg-paper/90">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between">
        <Link href="/" className="font-serif text-lg no-underline">
          CF Venture Opportunity Atlas
        </Link>
        <nav className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="no-underline hover:text-ink">
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
