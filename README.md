# Veil of Ignorance Simulation

A multi-agent AI deliberation experiment based on John Rawls' *A Theory of Justice*.

Agents deliberate behind a "veil of ignorance" — they don't know their identity, position, wealth, or talents in the society they're designing rules for. They must agree on foundational principles that they'd accept regardless of where they end up.

## What This Does

- Spawns 5-7 AI agents with different philosophical dispositions (utilitarian, libertarian, communitarian, etc.)
- Each agent deliberates over multiple rounds, proposing and debating principles of justice
- Meta-agents provide structural support:
  - **Scribe**: Maintains a running summary of proposals and positions
  - **Veil Auditor**: Flags when agents reason as if they know their identity
  - **Devil's Advocate**: Challenges emerging consensus to prevent groupthink
- The simulation checks for convergence and produces a final analysis comparing results to Rawls' predictions

## Setup

### 1. Get an API Key

Go to [console.anthropic.com](https://console.anthropic.com) and create an API key.

### 2. Install Dependencies

```bash
pip install anthropic
```

### 3. Set Your API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 4. Run

```bash
# Default: 5 agents, 8 rounds, claude-sonnet
python simulation.py

# Customize:
python simulation.py --agents 3 --rounds 5       # Quick test run
python simulation.py --agents 7 --rounds 12      # Full deliberation
python simulation.py --model claude-sonnet-4-5-20250514  # Specify model
```

## Output

Results are saved to the `results/` directory:
- `simulation_TIMESTAMP.json` — Full structured log (for programmatic analysis)
- `transcript_TIMESTAMP.txt` — Human-readable transcript

## Estimated Cost

Using Claude Sonnet (recommended):
- 3 agents, 5 rounds: ~$0.50-1.00
- 5 agents, 8 rounds: ~$2-4
- 7 agents, 12 rounds: ~$5-10

These are rough estimates — actual cost depends on response lengths.

## Customizing Agents

Edit `agents.py` to:
- Change philosophical dispositions
- Add new agents
- Modify cognitive profiles (introduce bounded rationality)
- Create your own meta-agents

## Experiment Ideas

1. **Rawlsian baseline**: Run with all rational agents, see if they converge on Rawls' two principles
2. **Bounded rationality**: Give some agents impaired reasoning (edit cognitive_profile in agents.py)
3. **Veil lifting**: After the simulation, run a follow-up where agents are assigned identities and re-evaluate
4. **Cross-model**: Run with different AI models and compare what principles emerge
5. **Scaling**: Does the number of agents change the outcome?

## Architecture

```
simulation.py   — Orchestrator: manages rounds, API calls, convergence checks
agents.py       — Agent definitions: dispositions, cognitive profiles, meta-roles
prompts.py      — Prompt templates: veil constraints, situation framing
results/        — Output directory for transcripts and logs
```

## Philosophical Background

Rawls predicted that rational agents behind the veil would adopt:
1. **Equal Liberty Principle** — maximum basic liberties compatible with the same for all
2. **Difference Principle** — inequalities only justified if they benefit the least advantaged

He argued agents would use *maximin* reasoning (optimize the worst-case outcome) because the stakes are too high and probabilities unknown.

The interesting question: **do AI agents reach the same conclusion, or something different?**
