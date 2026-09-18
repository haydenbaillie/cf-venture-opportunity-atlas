export const COMPONENTS = [
  "patient_need",
  "treatment_gap",
  "competitive_whitespace",
  "tractability",
  "economic",
  "why_now",
] as const;

export type ComponentId = (typeof COMPONENTS)[number];

export const COMPONENT_LABELS: Record<ComponentId, string> = {
  patient_need: "Patient need",
  treatment_gap: "Treatment gap",
  competitive_whitespace: "Competitive white space",
  tractability: "Tractability",
  economic: "Economic relevance",
  why_now: "Why now",
};

export const COMPONENT_HELP: Record<ComponentId, string> = {
  patient_need: "How big and severe is the leftover problem?",
  treatment_gap: "Do current options actually cover it?",
  competitive_whitespace: "Are companies already working here?",
  tractability: "Is the biology and endpoint even workable?",
  economic: "Chronic costly burden — not a market-size overlay",
  why_now: "Did something recently change?",
};

export const PRESET_LABELS: Record<string, string> = {
  default: "Default",
  patient_impact: "Patient impact",
  venture_creation: "Venture creation",
  commercial: "Commercial",
  custom: "Custom",
};

export const PRESET_HELP: Record<string, string> = {
  default: "The ranking used in the written memo",
  patient_impact: "Counts leftover burden more, emptiness less — restoration may move first",
  venture_creation: "Counts emptiness and workability more",
  commercial: "Counts payer logic and emptiness more",
  custom: "You moved a slider; weights still add to 100%",
};

export type Weights = Record<ComponentId, number>;

export function displayScore(value: number): number {
  return Math.round(value);
}

export function computeIndex(scores: Record<ComponentId, number>, weights: Weights): number {
  return 20 * COMPONENTS.reduce((sum, id) => sum + weights[id] * scores[id], 0);
}

export function normalizeWeights(weights: Weights): Weights {
  const total = COMPONENTS.reduce((sum, id) => sum + Math.max(0, weights[id]), 0);
  if (total <= 0) {
    const even = 1 / COMPONENTS.length;
    return Object.fromEntries(COMPONENTS.map((id) => [id, even])) as Weights;
  }
  return Object.fromEntries(
    COMPONENTS.map((id) => [id, Math.max(0, weights[id]) / total]),
  ) as Weights;
}

export function weightsFromRows(
  rows: { preset_id: string; component_id: string; weight: number }[],
  presetId: string,
): Weights {
  const next = {} as Weights;
  for (const row of rows) {
    if (row.preset_id === presetId && COMPONENTS.includes(row.component_id as ComponentId)) {
      next[row.component_id as ComponentId] = row.weight;
    }
  }
  return normalizeWeights(next);
}
