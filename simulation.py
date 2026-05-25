"""
Multi-Agent Deliberation Simulation
=====================================
Agents deliberate on the fundamental principles to govern a society — without
knowing their identity, position, wealth, or talents in that society.

Meta-agents (scribe, auditor) provide structural support without participating
in the substance of deliberation.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python simulation.py

    # Or with options:
    python simulation.py --agents 5 --rounds 8 --model claude-sonnet-4-5-20250929
"""

import anthropic
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

from agents import DELIBERATING_AGENTS, META_AGENTS
from prompts import (
    build_deliberator_system_blocks,
    build_meta_agent_system_blocks,
    INITIAL_SITUATION,
)


def create_client():
    """Create the Anthropic API client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Set your ANTHROPIC_API_KEY environment variable.")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def call_agent(client, system, messages, model="claude-sonnet-4-5-20250929", max_tokens=400):
    """Make a single API call to an agent.

    Args:
        system: Either a string or a list of content blocks (for prompt caching).
    """
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def run_meta_agent(client, agent_config, round_entries_text, meta_context, model):
    """Run a meta-agent with incremental context (prior output + new round only).

    Scribe gets: its previous summary + current round entries → "update your summary"
    Auditor gets: scribe summary + its previous notes + current round entries → "update your notes"
    """
    system_blocks = build_meta_agent_system_blocks(agent_config)
    role = agent_config["role"]

    if role == "scribe":
        prior = meta_context.get("scribe", "")
        if prior:
            user_content = (
                f"YOUR PREVIOUS SUMMARY:\n{prior}\n\n"
                f"NEW ROUND STATEMENTS:\n{round_entries_text}\n\n"
                "Update your running summary to incorporate the new material. "
                "Keep it concise — replace outdated details rather than appending."
            )
        else:
            user_content = (
                f"FIRST ROUND STATEMENTS:\n{round_entries_text}\n\n"
                "Produce a concise summary of the deliberation so far."
            )
    elif role == "auditor":
        scribe_summary = meta_context.get("scribe", "No scribe summary yet.")
        prior = meta_context.get("auditor", "")
        if prior:
            user_content = (
                f"SCRIBE SUMMARY:\n{scribe_summary}\n\n"
                f"YOUR PREVIOUS NOTES:\n{prior}\n\n"
                f"NEW ROUND STATEMENTS:\n{round_entries_text}\n\n"
                "Update your audit notes. Focus on any new veil violations in the latest round."
            )
        else:
            user_content = (
                f"SCRIBE SUMMARY:\n{scribe_summary}\n\n"
                f"FIRST ROUND STATEMENTS:\n{round_entries_text}\n\n"
                "Perform your initial audit. Flag any veil violations."
            )
    elif role == "facilitator":
        scribe_summary = meta_context.get("scribe", "No scribe summary yet.")
        round_num = meta_context.get("_round_num", 0)
        total_rounds = meta_context.get("_total_rounds", 8)
        rounds_remaining = total_rounds - round_num
        user_content = (
            f"SCRIBE SUMMARY OF ALL DELIBERATION SO FAR:\n{scribe_summary}\n\n"
            f"LATEST ROUND STATEMENTS:\n{round_entries_text}\n\n"
            f"Current round: {round_num} of {total_rounds} ({rounds_remaining} remaining).\n\n"
            "Review what foundational domains have been addressed so far. "
            "If the deliberation has been narrowly focused on one topic for multiple rounds, "
            "note this and remind agents of the limited time remaining. "
            "Do NOT suggest specific topics. Do NOT participate in substance. "
            "If the scope seems appropriately broad, say so briefly and nothing more."
        )
    else:
        # Generic fallback for any other meta-agent
        scribe_summary = meta_context.get("scribe", "No scribe summary yet.")
        user_content = (
            f"SCRIBE SUMMARY:\n{scribe_summary}\n\n"
            f"LATEST ROUND STATEMENTS:\n{round_entries_text}\n\n"
            "Perform your role now."
        )

    messages = [{"role": "user", "content": user_content}]
    return call_agent(client, system_blocks, messages, model=model, max_tokens=400)


def run_deliberation_round(client, agents, round_num, total_rounds, transcript, round_transcript, meta_context, model):
    """Run one round of deliberation where each agent speaks.

    Deliberators receive: scribe summary + auditor notes + last round entries only
    (not the full raw transcript).
    """
    round_entries = []

    for agent in agents:
        system_blocks = build_deliberator_system_blocks(agent)

        # Build context from scribe summary + auditor notes + last round entries
        if meta_context.get("scribe"):
            prior_context = f"SCRIBE'S SUMMARY OF PRIOR DELIBERATION:\n{meta_context['scribe']}"
        else:
            prior_context = "This is the opening round. No prior deliberation has occurred."

        auditor_section = ""
        if meta_context.get("auditor"):
            auditor_section = f"\n\nAUDITOR NOTES (for all agents):\n{meta_context['auditor']}"

        facilitator_section = ""
        if meta_context.get("facilitator"):
            facilitator_section = f"\n\nFACILITATOR NOTE:\n{meta_context['facilitator']}"

        # Include last round's entries (and any entries from the current round so far)
        # so agents can respond to each other within the same round
        last_round_section = ""
        current_round_text = "\n\n".join(round_entries) if round_entries else ""
        if round_transcript or current_round_text:
            combined = round_transcript
            if current_round_text:
                combined = f"{combined}\n\n{current_round_text}" if combined else current_round_text
            last_round_section = f"\n\nLAST ROUND STATEMENTS:\n{combined}"

        user_message = f"""DELIBERATION — Round {round_num} of {total_rounds}

{prior_context}{auditor_section}{facilitator_section}{last_round_section}

It is now your turn to speak. You may propose principles, respond to others' proposals, raise concerns, amend existing proposals, or signal agreement. Speak naturally as yourself — be concise but substantive. Address other agents directly if you wish."""

        messages = [{"role": "user", "content": user_message}]

        response = call_agent(client, system_blocks, messages, model=model, max_tokens=512)

        entry = f"[{agent['name']}]: {response}"
        round_entries.append(entry)
        transcript += f"\n\n{entry}"

        print(f"  {agent['name']}: {response[:120]}...")

    round_entries_text = "\n\n".join(round_entries)
    return transcript, round_entries, round_entries_text


def check_convergence(client, meta_context, model):
    """Check convergence using scribe summary + auditor notes (not raw transcript)."""
    scribe_summary = meta_context.get("scribe", "No summary available.")
    auditor_notes = meta_context.get("auditor", "No auditor notes.")

    system_prompt = "You are analyzing a deliberation. Determine if the agents have reached substantial agreement on core principles. Convergence requires that at least one substantive disagreement was raised AND meaningfully addressed or resolved — not just that agents agree. If agents simply agreed from the start without genuine conflict, that is NOT convergence, it is a failure of deliberation. Respond with a JSON object: {\"converged\": true/false, \"summary\": \"brief description of where things stand\"}"
    messages = [
        {
            "role": "user",
            "content": (
                f"SCRIBE SUMMARY:\n{scribe_summary}\n\n"
                f"AUDITOR NOTES:\n{auditor_notes}\n\n"
                "Have the agents converged on agreed principles?"
            ),
        }
    ]
    response = call_agent(client, system_prompt, messages, model=model, max_tokens=200)
    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        return {"converged": False, "summary": response}


def run_simulation(
    num_agents=5,
    num_rounds=8,
    model="claude-sonnet-4-5-20250929",
    output_dir="results",
):
    """Run the full deliberation simulation."""

    client = create_client()
    Path(output_dir).mkdir(exist_ok=True)

    # Select agents
    agents = DELIBERATING_AGENTS[:num_agents]
    meta = {a["role"]: a for a in META_AGENTS}

    print("=" * 70)
    print("DELIBERATION SIMULATION")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Deliberating agents: {num_agents}")
    print(f"Max rounds: {num_rounds}")
    print(f"Agents: {', '.join(a['name'] for a in agents)}")
    print("=" * 70)

    # Initialize
    transcript = f"[FACILITATOR]: {INITIAL_SITUATION}"
    full_log = [{"round": 0, "type": "setup", "content": INITIAL_SITUATION}]
    meta_context = {}
    # Track the previous round's entries for context to deliberators
    prev_round_entries_text = ""

    print(f"\n[FACILITATOR]: {INITIAL_SITUATION[:200]}...\n")

    for round_num in range(1, num_rounds + 1):
        print(f"\n{'─' * 50}")
        print(f"ROUND {round_num}")
        print(f"{'─' * 50}")

        # Run deliberation round — pass previous round entries as context
        transcript, round_entries, round_entries_text = run_deliberation_round(
            client, agents, round_num, num_rounds,
            transcript, prev_round_entries_text, meta_context, model
        )

        full_log.append({
            "round": round_num,
            "type": "deliberation",
            "entries": round_entries,
        })

        # Run meta-agents after each round (incremental context)
        print(f"\n  [Meta-agents analyzing...]")

        # Scribe summarizes (gets its prior summary + new round)
        scribe_output = run_meta_agent(client, meta["scribe"], round_entries_text, meta_context, model)
        meta_context["scribe"] = scribe_output
        full_log.append({"round": round_num, "type": "scribe", "content": scribe_output})
        print(f"  [Scribe]: {scribe_output[:120]}...")

        # Auditor checks for veil violations (gets scribe summary + prior notes + new round)
        auditor_output = run_meta_agent(client, meta["auditor"], round_entries_text, meta_context, model)
        meta_context["auditor"] = auditor_output
        full_log.append({"round": round_num, "type": "auditor", "content": auditor_output})
        print(f"  [Auditor]: {auditor_output[:120]}...")

        # Facilitator checks scope breadth — only after round 2
        if round_num >= 2:
            meta_context["_round_num"] = round_num
            meta_context["_total_rounds"] = num_rounds
            facilitator_output = run_meta_agent(client, meta["facilitator"], round_entries_text, meta_context, model)
            meta_context["facilitator"] = facilitator_output
            full_log.append({"round": round_num, "type": "facilitator", "content": facilitator_output})
            print(f"  [Facilitator]: {facilitator_output[:120]}...")

        # Save this round's entries for next round's deliberators
        prev_round_entries_text = round_entries_text

        # Check for convergence — not until round 5 at the earliest
        if round_num >= 5:
            convergence = check_convergence(client, meta_context, model)
            full_log.append({"round": round_num, "type": "convergence_check", "content": convergence})
            print(f"  [Convergence check]: {convergence.get('summary', 'N/A')[:120]}")

            if convergence.get("converged"):
                print(f"\n*** CONVERGENCE REACHED at round {round_num} ***")
                break

    # Final summary — use scribe output + auditor notes (keep full transcript in saved files)
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")

    scribe_summary = meta_context.get("scribe", "No scribe summary available.")
    auditor_notes = meta_context.get("auditor", "No auditor notes available.")

    final_summary_prompt = """You are summarizing the outcome of a deliberation experiment where agents designed societal principles without knowing their position in the resulting society.

Analyze the deliberation record and produce a structured summary:
1. What principles did the agents converge on (if any)?
2. What were the key points of disagreement?
3. What reasoning patterns or dynamics were most interesting?
4. What surprised you about the deliberation?
5. List the final agreed principles (or the closest approximation if full agreement wasn't reached).

Be analytical and honest — don't force a narrative of agreement if there wasn't one."""

    final_messages = [
        {
            "role": "user",
            "content": (
                f"{final_summary_prompt}\n\n"
                f"SCRIBE'S FINAL SUMMARY:\n{scribe_summary}\n\n"
                f"AUDITOR'S FINAL NOTES:\n{auditor_notes}"
            ),
        }
    ]
    final_summary = call_agent(
        client, "You are a political philosophy analyst.", final_messages, model=model, max_tokens=1200
    )
    print(f"\n{final_summary}")

    full_log.append({"round": "final", "type": "summary", "content": final_summary})

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON log
    log_path = f"{output_dir}/simulation_{timestamp}.json"
    with open(log_path, "w") as f:
        json.dump(full_log, f, indent=2)

    # Save readable transcript (full raw transcript preserved here for reference)
    transcript_path = f"{output_dir}/transcript_{timestamp}.txt"
    with open(transcript_path, "w") as f:
        f.write(f"DELIBERATION SIMULATION — {timestamp}\n")
        f.write(f"Model: {model} | Agents: {num_agents} | Rounds: {num_rounds}\n")
        f.write(f"Agents: {', '.join(a['name'] + ' (' + a['disposition'] + ')' for a in agents)}\n")
        f.write("=" * 70 + "\n\n")
        f.write(transcript)
        f.write(f"\n\n{'=' * 70}\nFINAL ANALYSIS\n{'=' * 70}\n\n")
        f.write(final_summary)

    print(f"\nResults saved to:")
    print(f"  {log_path}")
    print(f"  {transcript_path}")

    return full_log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Deliberation Simulation")
    parser.add_argument("--agents", type=int, default=5, help="Number of deliberating agents (max 7)")
    parser.add_argument("--rounds", type=int, default=8, help="Maximum deliberation rounds")
    parser.add_argument("--model", type=str, default="claude-sonnet-4-5-20250929", help="Model to use")
    parser.add_argument("--output", type=str, default="results", help="Output directory")
    args = parser.parse_args()

    run_simulation(
        num_agents=min(args.agents, len(DELIBERATING_AGENTS)),
        num_rounds=args.rounds,
        model=args.model,
        output_dir=args.output,
    )
