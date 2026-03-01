---
name: bridge-gemini
description: Reference adapter for Gemini CLI. Read by any orchestrating skill via the Read tool. Defines how to invoke Gemini CLI in non-interactive mode, timeout estimation, and fallback behavior. Usable by deep-council, deep-review, deep-audit, or any future skill that needs Gemini-based review.
location: managed
context: reference
---

# Bridge: Gemini CLI Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Gemini CLI dispatch.

**Input schema, agent prompt template, output schema, verdict logic, timeout formula, artifact format, and status semantics are defined in `bridge-commons/SKILL.md`. This file covers only Gemini-specific connection detection and execution.**

## Bridge Identity

```yaml
bridge: gemini
model_family: google/gemini
availability: conditional
connection_preference:
  1: native-dispatch  # Executor is Gemini CLI — Gemini subagents (enableAgents)
  2: cli              # Any other executor — gemini -p
  3: skip             # Neither — return SKIPPED (non-blocking)
```

---

## Pre-Flight — Connection Detection

### Check A: Native Dispatch?

If the executor is Gemini CLI with subagent support enabled, this is the preferred path — spawn specialized Gemini subagents rather than shelling out to the CLI.

```bash
# Check if subagents are enabled in project or user settings
cat .gemini/settings.json 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('experimental',{}).get('enableAgents', False))"

# Also check user-level settings
cat ~/.gemini/settings.json 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('experimental',{}).get('enableAgents', False))"
```

If `True` and the current executor is Gemini CLI → **use native dispatch** (subagent path in Subagent Mode section).

If executor is not Gemini, or `enableAgents` is `false` or missing → proceed to Check B.

---

### Check B: CLI Installed?

```bash
which gemini
```

If found → **use CLI path** (Execution section).

If not found → return immediately:

```json
{
  "bridge": "gemini",
  "status": "SKIPPED",
  "skip_reason": "gemini CLI not available (which gemini returned empty)",
  "outputs": [],
  "verdict": null
}
```

Never fail or block — SKIPPED is a valid bridge outcome.

---

## Execution

Build the prompt using the Agent Prompt Template from bridge-commons, adapting to `task_type`. Calculate timeout using bridge-commons formula (no bridge-specific multiplier for Gemini).

```bash
TIMEOUT={calculated_timeout}
PROMPT="{constructed_prompt}"

timeout $TIMEOUT gemini -p "$PROMPT" --approval-mode auto_edit --output-format json
```

Error handling:
- Exit code 0 with JSON → parse and return findings
- Exit code 124 (timeout) → return SKIPPED with reason `timeout_after_{n}s`
- Other exit codes → return SKIPPED with reason `gemini CLI error: {stderr}`
- Invalid JSON output → attempt to extract structured content, else SKIPPED

After execution, run the bridge-commons Post-Analysis Protocol. Gemini uses **stateless context passing** between rounds — embed the full previous-round outputs and context packet in each subsequent `gemini -p` call. There is no session continuity between separate CLI invocations.

For `standard` and `thorough` intensity, construct the Round 2 prompt as:

```
{Agent Prompt Template for this role}

--- ROUND 2 CONTEXT ---
Previous round findings:
{JSON of all Round 1 outputs}

{context packet: open_challenges directed at this domain, synthesis}
```

**Never block the calling orchestrator** — always return a report (even if SKIPPED).

---

## Subagent Mode

Gemini CLI supports custom subagents for parallel domain dispatch when `experimental.enableAgents` is set in `.gemini/settings.json`.

```bash
# Confirm subagents are enabled
cat .gemini/settings.json 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('experimental',{}).get('enableAgents', False))"
```

- If `true` → spawn one subagent per domain; run consolidation pass after all complete
- If `false` or missing → run standard single Gemini call covering all domains (valid fallback)

Subagent mode is a progressive enhancement. Record `subagent_mode: true/false` in output.

---

## Output

See bridge-commons Output Schema. Bridge-specific fields:

```json
{
  "bridge": "gemini",
  "model_family": "google/gemini",
  "connection_used": "native-dispatch | cli",
  "subagent_mode": true
}
```

Output ID prefix: `G` (e.g., `G001`, `G002`).

---

## Notes

- Always check availability first — never assume gemini is installed
- Use non-interactive mode only (`--approval-mode auto_edit`; `plan` is experimental and unreliable)
- Use `--output-format json` for structured parsing (not `-o json`)
- Timeout is estimated from scope, not hardcoded — see bridge-commons formula
- SKIPPED is a valid, non-error outcome
