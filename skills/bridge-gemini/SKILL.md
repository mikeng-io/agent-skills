---
name: bridge-gemini
description: Reference adapter for Gemini CLI. Read by deep-council via Read tool. Defines how to invoke Gemini CLI in non-interactive mode, timeout estimation, fallback behavior. NOT invocable standalone — context: reference.
location: managed
context: reference
---

# Bridge: Gemini CLI Adapter

This file is a REFERENCE DOCUMENT. It is read by `deep-council` via the `Read` tool and its instructions are embedded directly into Task agent prompts. Do not invoke it as a standalone skill.

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
    "review_id": "...",
    "review_scope": "Files and/or description of what to review",
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

Build the Gemini review prompt from bridge_input:

```
You are reviewing the following for potential issues:

SCOPE: {review_scope}

CONTEXT: {context_summary}

DOMAINS TO CHECK: {domains joined with ", "}

INTENSITY: {intensity}

Please analyze for issues in each domain. For each finding, provide:
- severity: CRITICAL | HIGH | MEDIUM | LOW | INFO
- title: Short finding title
- description: Detailed description
- evidence: Specific reference
- remediation: How to fix
- domain: Which domain this belongs to

Return your findings as a JSON array in this format:
{
  "findings": [...],
  "overall_assessment": "...",
  "verdict": "PASS | FAIL | CONCERNS"
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
  "review_id": "...",
  "status": "COMPLETED | SKIPPED",
  "skip_reason": "...",
  "domains_covered": [],
  "findings": [
    {
      "id": "GF001",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "...",
      "domain": "..."
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "timeout_used": 180,
  "confidence": "high | medium | low"
}
```

## Notes

- Always check availability first — never assume gemini is installed
- Use non-interactive mode only (`--approval-mode plan`)
- JSON output flag `-o json` for structured parsing
- Timeout is ESTIMATED not hardcoded — recalculate per scope
- SKIPPED is a valid, non-error outcome
