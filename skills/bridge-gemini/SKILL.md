---
name: bridge-gemini
description: Reference adapter for Gemini CLI. Read by any orchestrating skill via the Read tool. Defines how to invoke Gemini CLI in non-interactive mode, timeout estimation, and fallback behavior. Usable by deep-council, deep-review, deep-audit, or any future skill that needs Gemini-based review.
location: managed
context: reference
---

# Bridge: Gemini CLI Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Gemini CLI dispatch.

## Bridge Identity

```yaml
bridge: gemini
model_family: google/gemini
availability: conditional   # Requires gemini CLI
connection: cli             # gemini -p "..." --approval-mode plan -o json
availability_check: "which gemini"
```

## Availability Check

Before executing, the bridge executor MUST check:

```bash
which gemini
```

If gemini is not found → return immediately:
```json
{
  "bridge": "gemini",
  "status": "SKIPPED",
  "reason": "gemini CLI not available (which gemini returned empty)",
  "findings": [],
  "verdict": null
}
```

Never fail or block — SKIPPED is a valid bridge outcome.

## Input Format

```json
{
  "bridge_input": {
    "session_id": "...",
    "scope": "Files and/or description of what to work on",
    "task_description": "What the agent should do (review, plan, implement, analyze, etc.)",
    "task_type": "review | planning | implementation | analysis | research",
    "domains": ["domain1", "domain2"],
    "context_summary": "What the conversation/task is about",
    "intensity": "quick | standard | thorough"
  }
}
```

## Timeout Estimation

**IMPORTANT: Do NOT use hardcoded timeouts.** Estimate based on review scope:

```yaml
scope_under_5_files_or_500_loc:
  base_timeout: 60   # seconds

scope_5_to_20_files_or_2000_loc:
  base_timeout: 180

scope_20_to_50_files_or_10k_loc:
  base_timeout: 300

scope_50_plus_files_or_10k_plus_loc:
  base_timeout: 600

intensity_multiplier:
  quick: 0.5        # Faster, less depth
  standard: 1.0     # Baseline
  thorough: 1.5     # More depth = more time
```

Final timeout = `base_timeout * intensity_multiplier`

## Prompt Construction

Build the Gemini prompt from bridge_input. Adapt based on `task_type`:

```
You are a multi-domain expert. Your task: {task_description}

SCOPE: {scope}
CONTEXT: {context_summary}
TASK TYPE: {task_type}
DOMAINS: {domains joined with ", "}
INTENSITY: {intensity}

For each domain, act as the corresponding domain expert. For each output item, provide:
- type: finding | recommendation | plan-item | implementation-note | observation
- severity: CRITICAL | HIGH | MEDIUM | LOW | INFO  (for review/analysis types)
- title: Short title
- description: Detailed description
- evidence: Specific reference
- action: Recommended action
- domain: Which domain this belongs to

Return as JSON:
{
  "outputs": [...],
  "summary": "...",
  "verdict": "PASS | FAIL | CONCERNS | null"
}
```

## Execution

```bash
TIMEOUT={calculated_timeout}
PROMPT="{constructed_prompt}"

timeout $TIMEOUT gemini -p "$PROMPT" --approval-mode plan -o json
```

Error handling:
- Exit code 0 with JSON → parse and return findings
- Exit code 124 (timeout) → return SKIPPED with reason "timeout after {n}s"
- Other exit codes → return SKIPPED with reason "gemini CLI error: {stderr}"
- Invalid JSON output → attempt to extract structured content, else SKIPPED

**Never block the calling orchestrator** — always return a report (even if SKIPPED).

## Output Format

```json
{
  "bridge": "gemini",
  "model_family": "google/gemini",
  "session_id": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "status": "COMPLETED | SKIPPED",
  "skip_reason": "...",
  "subagent_mode": true,
  "domains_covered": [],
  "outputs": [
    {
      "id": "G001",
      "type": "finding | recommendation | plan-item | implementation-note | observation",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "action": "...",
      "domain": "..."
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "timeout_used": 180,
  "confidence": "high | medium | low"
}
```

## Subagent Mode (Optional)

Gemini CLI supports custom subagents for parallel domain dispatch when `experimental.enableAgents` is set in `.gemini/settings.json`.

```bash
# Check if subagents are enabled
cat .gemini/settings.json 2>/dev/null | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('experimental',{}).get('enableAgents', False))"
```

- If `true` → spawn one subagent per domain (see `cli-reference.md` for custom agent definition)
- If `false` or missing → run standard single Gemini call covering all domains (valid fallback)

Subagent mode is a progressive enhancement. Record `subagent_mode: true/false` in output.

## Notes

- Always check availability first — never assume gemini is installed
- Use non-interactive mode only (`--approval-mode plan`)
- JSON output flag `-o json` for structured parsing
- Timeout is estimated from scope, not hardcoded — recalculate per review
- SKIPPED is a valid, non-error outcome
