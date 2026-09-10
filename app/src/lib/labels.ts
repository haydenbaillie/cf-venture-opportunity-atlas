export const STRATEGY_LABELS: Record<string, string> = {
  anion_bypass: "Anion bypass",
  anti_inflammatory: "Anti-inflammatory",
  antimicrobial: "Antimicrobial",
  aso_oligonucleotide: "ASO / splicing",
  cftr_modulator: "CFTR modulator",
  gene_editing: "Gene editing",
  gene_therapy: "Gene therapy",
  genetic_therapy: "Genetic therapy",
  gi_nutrition: "GI / nutrition",
  metabolic_cfrd: "CFRD / metabolic",
  mrna: "mRNA",
  mucociliary_clearance: "Mucociliary",
  nonsense_readthrough: "Nonsense readthrough",
  other: "Other",
  phage: "Phage",
};

export const STAGE_LABELS: Record<string, string> = {
  preclinical: "Preclinical",
  phase_1: "Ph1",
  phase_2: "Ph2",
  phase_3: "Ph3",
  approved: "Approved",
  standard_of_care: "SoC",
};

export const STAGES = [
  "preclinical",
  "phase_1",
  "phase_2",
  "phase_3",
  "approved",
  "standard_of_care",
] as const;

export const STANCE_LABELS: Record<string, string> = {
  pursue_diligence: "Pursue diligence",
  watch_adjacent: "Watch adjacent",
  watch_incumbents: "Watch incumbents",
  services_not_drug: "Services, not a drug",
};
