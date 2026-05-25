# Experiment Log

Notes and observations across simulation runs. Each entry records what changed, what happened, and what it suggests.

---

## Run 2026-05-24 #2 — "Higher-level prompt"

**Change:** Replaced "Propose specific principles when you can, not just abstract sentiments" with "Propose principles at the level of constitutional foundations — the kind of commitments that could guide a society for centuries — not specific policy details like tax rates or enforcement budgets."

**Result:** Dramatically different deliberation character. Agents stayed at the level of constitutional principles rather than drafting tax law.

| | Previous runs | This run |
|---|---|---|
| Core debate | "15% or 10%?" | "What justifies institutional authority at all?" |
| Breakthrough | Math forcing honest tradeoffs | The "infant problem" — Delta's libertarianism collapsed when confronted with helpless dependents who can't participate in voluntary exchange |
| Outcome | Narrow child-support system (4-1 split) | Broad constitutional framework with constraint stacking (5-0, Epsilon noting incompleteness) |
| Veil violations | Gamma flagged 6 rounds (Feb runs) | Zero across all 8 rounds |

**Key finding:** Agents converged through "constraint proliferation" — stacking safeguards (veto power, supermajority, opposed incentives, narrow scope) until everyone felt protected from their worst fear. Epsilon's meta-observation: they built a cage and called it a constitution.

**Takeaway:** A single prompt line steered agents from legislative drafting to philosophical reasoning. The "specificity" instruction was the main driver of pedantic behavior, not the agents' natural tendency.

---

## Run 2026-05-24 #1 — Baseline (current prompts, pre-tweak)

**Change:** None — ran existing prompts to get a fresh baseline.

**Result:** Agents converged on fiscal mechanics: 25% GDP floor, 40-45% cap, 75% supermajority protections. Split 3-2 on narrow vs. broad coverage (chronic disease debate). Zero veil violations. Heavy focus on enforcement math — agents demanded cost calculations and caught each other proposing systems that broke their own caps.

**Takeaway:** Consistent with February runs. Agents default to institutional mechanics and specific numbers when prompted for "specific principles."

---

## Runs 2026-02-05 (x4) — Original experiments

**Setup:** 5 agents, 8 rounds, Claude Sonnet. Original prompts with "propose specific principles" instruction.

**Result:** Best documented run converged 4-1 on a minimalist child-support system: 15% extraction, children under 10 only, local administration under 150 people, 8-year sunset, absolute cap. Agent Gamma flagged by Veil Auditor for 6 consecutive rounds of reasoning from the producer's perspective.

**Key findings:**
- No agent argued for zero collective obligation — the veil made pure voluntarism feel too risky
- Agents prioritized anti-corruption mechanics over moral scope
- Gamma's veil violations didn't produce bad conclusions, just compromised reasoning — suggesting the veil makes bias visible even when it doesn't eliminate it
