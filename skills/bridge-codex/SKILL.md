---
name: bridge-codex
description: Reference adapter for Codex CLI. Read by deep-council via Read tool. Defines MCP→CLI fallback chain, timeout estimation, read-only enforcement. NOT invocable standalone — context: reference.
location: managed
context: reference
---

# Bridge: Codex Adapter

This file is a REFERENCE DOCUMENT. It is read by `deep-council` via the `Read` tool and its instructions are embedded directly into Task agent prompts.

## Bridge Identity

```yaml
bridge: codex
model_family: openai/codex
availability: conditional   # MCP or CLI
connection_chain:
  1: mcp    # Check .mcp.json for codex server config
  2: cli    # codex --approval-policy never -p "{prompt}"
  3: skip   # If neither available
```

## Connection Detection (Fallback Chain)

### Option 1: MCP Connection

Check if Codex MCP server is configured:
```bash
# Look for codex in MCP config
cat .mcp.json 2>/dev/null | grep -i codex
# OR check Claude's MCP settings
```

If MCP server found → use `mcp__codex__codex` tool.

### Option 2: CLI Connection

```bash
which codex
```

If found → use CLI: `codex --approval-policy never -p "{prompt}"`

### Option 3: Skip

If neither MCP nor CLI available:
```json
{
  "bridge": "codex",
  "status": "SKIPPED",
  "reason": "No Codex connection available (MCP not configured, CLI not found)"
}
```

## Mandated Parameters

**REQUIRED on both MCP and CLI paths:**

```yaml
mcp_path:
  approval_policy: never    # Read-only enforcement
  model: "gpt-5.3-codex"   # Or latest available

cli_path:
  approval_policy: "--approval-policy never"
  model: "--model gpt-5.3-codex"  # Or latest available
```

The `never` approval policy ensures Codex operates in read-only analysis mode only.

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

Estimate based on scope (same scale as bridge-gemini):

```yaml
scope_under_5_files_or_500_loc:    base_timeout: 60
scope_5_to_20_files_or_2000_loc:   base_timeout: 180
scope_20_to_50_files_or_10k_loc:   base_timeout: 300
scope_50_plus_files_or_10k_plus:   base_timeout: 600

intensity_multiplier:
  quick: 0.5
  standard: 1.0
  thorough: 1.5
```

For MCP calls: pass as timeout parameter.
For CLI calls: use shell `timeout {n}` wrapper.

## Prompt Construction

```
Review the following for issues:

SCOPE: {review_scope}
CONTEXT: {context_summary}
DOMAINS: {domains}
INTENSITY: {intensity}

Analyze for issues in each domain. Return JSON with findings array.
Each finding: severity, title, description, evidence, remediation, domain.
Verdict: PASS | FAIL | CONCERNS
```

## Execution

### MCP Path

```
Call: mcp__codex__codex
Parameters:
  prompt: {constructed_prompt}
  approval_policy: "never"
  model: "gpt-5.3-codex"
  timeout: {calculated_timeout}
```

### CLI Path

```bash
timeout {calculated_timeout} codex --approval-policy never \
  --model gpt-5.3-codex \
  -p "{constructed_prompt}"
```

## Output Format

```json
{
  "bridge": "codex",
  "model_family": "openai/codex",
  "connection_used": "mcp | cli",
  "review_id": "...",
  "status": "COMPLETED | SKIPPED",
  "skip_reason": "...",
  "domains_covered": [],
  "findings": [
    {
      "id": "CF001",
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

- Always try MCP first (lower latency, better integration)
- CLI is reliable fallback if MCP not configured
- `--approval-policy never` is NON-NEGOTIABLE — read-only only
- Timeout is calculated, never hardcoded
- SKIPPED is a valid non-error outcome
