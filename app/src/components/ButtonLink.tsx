import Link from "next/link";

export default function ButtonLink({
  href,
  children,
  tone = "accent",
}: {
  href: string;
  children: React.ReactNode;
  tone?: "accent" | "plain";
}) {
  const classes =
    tone === "accent"
      ? "inline-block border border-accent bg-accent px-3 py-2 text-sm text-white no-underline hover:opacity-90"
      : "inline-block border border-mist bg-white px-3 py-2 text-sm text-ink no-underline hover:border-accent";
  return (
    <Link href={href} className={classes}>
      {children}
    </Link>
  );
}
