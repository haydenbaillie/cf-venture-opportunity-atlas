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
  phase_1: "Phase 1",
  phase_2: "Phase 2",
  phase_3: "Phase 3",
  approved: "Approved",
  standard_of_care: "Standard of care",
};

export const STAGE_HELP: Record<string, string> = {
  preclinical: "Not yet tested in people",
  phase_1: "First safety studies in people",
  phase_2: "Early signal of whether it works",
  phase_3: "Large confirmatory studies",
  approved: "Regulators have said yes",
  standard_of_care: "What clinics already use",
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

export const STANCE_HELP: Record<string, string> = {
  pursue_diligence: "Worth a closer look — not a mandate to form a company",
  watch_adjacent: "A drug for a nearby disease might close this gap first",
  watch_incumbents: "Large companies are already in this race",
  services_not_drug: "A clinic or operations problem, not a new medicine",
};

export const NEED_IDS = ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"] as const;

export const NEED_LABELS: Record<string, string> = {
  N1: "Mutation-agnostic CFTR restoration",
  N2: "Eligible but not prescribed",
  N3: "Residual lung disease",
  N4: "Chronic infection",
  N5: "CFRD / diabetes and metabolism",
  N6: "GI and CF liver disease",
  N7: "Aging with CF",
  N8: "Treatment burden and care delivery",
};

export const NEED_BLURBS: Record<string, string> = {
  N1: "Treatments meant to work regardless of which CF gene mutations a person has",
  N2: "People who could take a modulator but did not fill a prescription",
  N3: "Lung flares and breathing impairment that remain after modulators",
  N4: "Persistent airway bacteria such as Pseudomonas and NTM",
  N5: "CF-related diabetes, which is common in adults",
  N6: "Pancreatic enzymes are a solved product class; advanced liver disease is not",
  N7: "People with CF now live into older adulthood — a demographic fact, not one drug target",
  N8: "Clinic visits and daily inhaled therapies that remain after modulators",
};

export const LAYER_HELP: Record<string, string> = {
  FACT: "A published number with a source and a date. You can check it.",
  ANALYSIS: "A filter or count this project computed, such as the reviewed CF map.",
  INTERPRETATION: "What we think the fact and analysis mean. Not a score yet.",
  HYPOTHESIS: "A score or thesis. Always shown with evidence and a way to kill it.",
};

export function needLabel(id: string) {
  return NEED_LABELS[id] ? `${id} · ${NEED_LABELS[id]}` : id;
}
