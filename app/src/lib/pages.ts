export const PAGES = [
  { href: "/", label: "Home", hint: "The question this site asks" },
  { href: "/landscape", label: "Landscape", hint: "What has been solved, and what is still leftover" },
  { href: "/pipeline", label: "Pipeline", hint: "Why a raw trial search is not the competitive map" },
  { href: "/map", label: "Map", hint: "Which leftovers already have companies" },
  { href: "/opportunities", label: "Opportunities", hint: "Ranked leftovers and theses you can kill" },
  { href: "/methodology", label: "Methodology", hint: "Sources, scoring rules, and limits" },
] as const;

export type PageHref = (typeof PAGES)[number]["href"];
