export default function Note({
  title,
  children,
}: {
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <aside className="border border-mist bg-white p-5">
      {title ? <h2 className="font-serif text-xl text-ink">{title}</h2> : null}
      <div className={`max-w-3xl space-y-2 text-sm text-muted ${title ? "mt-2" : ""}`}>
        {children}
      </div>
    </aside>
  );
}
