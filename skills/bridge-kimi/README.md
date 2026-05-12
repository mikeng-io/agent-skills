# Bridge: Kimi Code

Reference adapter for Kimi Code CLI dispatch. Part of the Deep Skills Suite bridge layer.

## What is this?

This is a **reference document**, not a runnable skill. Any orchestrating skill reads `SKILL.md` via the `Read` tool and embeds its instructions into Task agent prompts. The bridge defines how to invoke Kimi CLI as an external reviewer.

## How it works

1. An orchestrating skill reads `bridge-kimi/SKILL.md`
2. Spawns a Task agent (the "bridge executor") with these instructions embedded
3. Bridge executor invokes `kimi --print -p "..." --afk` (or native subagents when inside Kimi)
4. Bridge executor collects findings and returns a `bridge_kimi_report`
5. The calling skill receives the report for synthesis

## Availability

Conditional — depends on what's available to the executor:

1. **Native subagents** — when Kimi CLI is the executor and Agent tool is accessible (`coder`, `explore`, `plan` types)
2. **Kimi CLI** (`which kimi`) — when any executor can shell out to `kimi --print -p`; requires auth via `KIMI_API_KEY` or prior `kimi login`
3. **SKIPPED** — none of the above available

Bridge-kimi is non-blocking — it returns SKIPPED if Kimi is not installed or not authenticated.

## Output

Returns a `bridge_kimi_report` JSON with findings, verdict, and confidence level.

Output ID prefix: `K` (e.g., `K001`, `K002`).

## Part of

- Deep Skills Suite
- Consumed by: any orchestrating skill (e.g., `deep-council`, `deep-review`, `deep-audit`, or custom skills)
- Depends on: `domain-registry` (for expert role selection)
