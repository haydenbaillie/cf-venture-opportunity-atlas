import snapshot from "@/data/snapshot.json";

export function claim(id: string) {
  const row = snapshot.claims.find((item) => item.claim_id === id);
  if (!row) throw new Error(`Missing claim ${id}`);
  return row;
}

export function summary(metric: string) {
  const row = snapshot.classification_summary.find((item) => item.metric === metric);
  if (!row) throw new Error(`Missing summary ${metric}`);
  return row;
}

export function thesis(id: string) {
  const row = snapshot.theses.find((item) => item.thesis_id === id);
  if (!row) throw new Error(`Missing thesis ${id}`);
  return row;
}

export function fmt(value: number, digits = 0) {
  return value.toLocaleString("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

export function fmtDate(iso: string) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-US", { day: "numeric", month: "short", year: "numeric" });
}
