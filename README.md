# Veil of Ignorance: A Multi-Agent Deliberation Experiment

What happens when you strip AI agents of identity and ask them to design a just society from scratch?

This is an implementation of John Rawls' "original position" thought experiment using multiple Claude agents. Each agent deliberates behind a veil of ignorance — they don't know their race, wealth, talents, or position in the society they're designing. They must propose and negotiate principles they'd accept *regardless of where they end up*.

## Why I Built This

I'm interested in a question at the intersection of AI and political philosophy: **can impartiality be architecturally imposed on language models?**

LLMs absorb the biases of their training data. They've seen the world from many perspectives, but those perspectives aren't evenly distributed. If you ask an LLM to "design a fair society," you get something shaped by whichever voices dominate the corpus. The output *looks* impartial but isn't — it's a weighted average of existing opinions dressed up as neutrality.

Rawls' veil of ignorance offers a structural solution: don't ask agents to *be* impartial — make it *irrational* for them to be anything else. If you genuinely don't know whether you'll be rich or poor, healthy or disabled, majority or minority, self-interest and fairness converge.

This simulation tests whether that works in practice. Can prompt engineering create genuine epistemic constraints? Do agents actually reason differently when their identity is unknown? Or do they leak assumptions and smuggle in perspectives despite the veil?

The answer turns out to be: mostly yes, with interesting failures. One agent (the libertarian-leaning "Gamma") was flagged by the Veil Auditor for six consecutive rounds of reasoning from the producer's perspective — subtly assuming it would be the one being "extracted from" rather than the one in need. Yet it still reached defensible conclusions. The veil doesn't eliminate bias, but it makes bias *visible and arguable*.

## What Emerged

Across multiple runs, agents consistently:

- **Accepted redistribution as legitimate** — no agent argued for zero collective obligation, even the libertarian. The veil made pure voluntarism feel too risky.
- **Prioritized enforcement mechanics over moral scope** — rather than designing comprehensive coverage, agents spent most rounds debating *how to prevent the system from being corrupted*. They feared institutional capture more than insufficient generosity.
- **Converged on minimalism with sunset clauses** — the final framework was deliberately narrow (protecting only children under 10) with mandatory 8-year review periods. Agents chose guaranteed protection for one verifiable category over theoretical protection for many.
- **Split 4-1 on a genuinely hard question** — whether to extend coverage to disabled adults, knowing it requires discretionary judgment about who qualifies. The dissenter made the most morally urgent argument but couldn't solve the enforcement problem.

The most surprising finding: agents invented something closer to a *constitutional convention* than Rawls' two principles. They didn't derive abstract maxims — they negotiated specific percentages, enforcement mechanisms, and institutional constraints. The deliberation felt more like drafting legislation than doing philosophy.

## How It Works

Five to seven agents with distinct philosophical dispositions (utilitarian, libertarian, communitarian, etc.) deliberate over multiple rounds. Three meta-agents provide structural support without participating in substance:

- **Scribe** — maintains a running summary of proposals and positions
- **Veil Auditor** — flags when agents reason as if they know their identity (the most interesting role — it catches subtle perspective-leaking)
- **Facilitator** — tracks whether the deliberation is getting stuck on one topic and reminds agents of time constraints

The simulation checks for convergence after round 5 and produces a final analysis.

Agents are explicitly prohibited from referencing any philosopher or academic theory — they must reason from first principles. This prevents them from just reciting Rawls back at you.

## Running It

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"

# Default: 5 agents, 8 rounds
python simulation.py

# Quick test
python simulation.py --agents 3 --rounds 5

# Full deliberation
python simulation.py --agents 7 --rounds 12
```

Results land in `results/` as both JSON (for programmatic analysis) and readable transcripts.

**Cost:** ~$2-4 for a standard run (5 agents, 8 rounds, Claude Sonnet).

## Architecture

```
simulation.py   — Orchestrator: manages rounds, convergence, API calls
agents.py       — Agent definitions: dispositions, cognitive profiles, meta-roles
prompts.py      — Prompt templates: veil constraints, situation framing
results/        — Transcripts and structured logs from prior runs
```

The prompt architecture uses a layered system: a static "veil constraints" block (cached for efficiency) defines what agents don't know, while per-round context gives them only the scribe's summary and auditor's notes rather than the full transcript. This keeps token usage manageable while preserving deliberation continuity.

## Experiment Ideas

- **Cross-model comparison** — do different model families produce different political philosophies?
- **Veil lifting** — after deliberation, assign agents identities and see if they'd still accept their own principles
- **Bounded rationality** — give some agents impaired reasoning (one agent already has this: "tends toward satisficing, impatient with abstraction")
- **Scaling** — does the number of agents change convergence patterns?
- **Adversarial agents** — add an agent secretly trying to smuggle in self-interested principles

## The Bigger Question

This is ultimately a project about AI alignment by another name. The veil of ignorance is a *mechanism for producing fair outcomes from self-interested agents* — which is exactly the alignment problem restated in political philosophy terms.

If we can architecturally constrain AI agents to reason impartially — not by training them to say fair things, but by making it structurally irrational to favor any particular position — that's a different kind of safety guarantee than RLHF or constitutional AI. It's fairness through game theory rather than fairness through instruction-following.

Whether it actually works at scale is an open question. But watching agents negotiate, compromise, dissent, and ultimately produce something that looks like constitutional law — without being told to — suggests the approach has legs.
