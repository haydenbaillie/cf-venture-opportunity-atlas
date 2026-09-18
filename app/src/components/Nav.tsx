"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PAGES } from "@/lib/pages";

export default function Nav() {
  const pathname = usePathname();

  return (
    <header className="border-b border-mist bg-paper/90">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between">
        <Link href="/" className="font-serif text-lg no-underline">
          CF Venture Opportunity Atlas
        </Link>
        <nav className="flex flex-wrap gap-x-4 gap-y-2 text-sm" aria-label="Main">
          {PAGES.map((link) => {
            const active =
              link.href === "/" ? pathname === "/" : pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={`no-underline hover:text-ink ${active ? "text-ink" : "text-muted"}`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
