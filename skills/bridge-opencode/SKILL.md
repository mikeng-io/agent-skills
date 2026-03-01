---
name: bridge-opencode
description: Reference adapter for OpenCode — model-agnostic multi-model bridge. Read by any orchestrating skill via the Read tool. Defines MCP/API→CLI fallback, multi-model configuration, and timeout estimation (1.5× multiplier). Usable by deep-council, deep-review, deep-audit, or any future skill that needs multi-model review.
location: managed
context: reference
---

# Bridge: OpenCode Multi-Model Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for OpenCode multi-model dispatch.

## Bridge Identity

```yaml
bridge: opencode
model_family: multi-model   # OpenCode dispatches to multiple models internally
availability: conditional
connection_chain:
  1: mcp-api   # Check .mcp.json for opencode server config
  2: cli       # opencode run --prompt "{prompt}" --no-interactive
  3: skip
```

## Why OpenCode is Special

OpenCode is the highest-coverage single bridge because it dispatches to multiple model families internally. A single OpenCode call can provide perspectives from GLM, Qwen, MiniMax, and other models simultaneously.

**Trade-off:** Higher latency due to multi-model internal dispatch. Use a 1.5× timeout multiplier.

## Connection Detection (Fallback Chain)

### Option 1: MCP/API Connection

```bash
cat .mcp.json 2>/dev/null | grep -i opencode
```

If OpenCode MCP server configured → use via MCP API.

### Option 2: CLI Connection

```bash
which opencode
```

If found → use: `opencode run --prompt "{prompt}" --no-interactive`

### Option 3: Skip

```json
{
  "bridge": "opencode",
  "status": "SKIPPED",
  "reason": "No OpenCode connection available"
}
```

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

OpenCode has a **1.5× multiplier** on top of the base scope timeout (multi-model overhead):

```yaml
scope_under_5_files_or_500_loc:    base_timeout: 60
scope_5_to_20_files_or_2000_loc:   base_timeout: 180
scope_20_to_50_files_or_10k_loc:   base_timeout: 300
scope_50_plus_files_or_10k_plus:   base_timeout: 600

opencode_multiplier: 1.5   # Always applied — multi-model internal dispatch

intensity_multiplier:
  quick: 0.5
  standard: 1.0
  thorough: 1.5

final_timeout: base_timeout * 1.5 * intensity_multiplier
```

## Multi-Model Configuration

### MCP/API path

Pass model list if API accepts it:
```json
{
  "models": ["glm", "qwen", "minimax"],
  "prompt": "{constructed_prompt}"
}
```

### CLI path

Pass model configuration as CLI arguments if supported:
```bash
opencode run --prompt "{prompt}" --no-interactive \
  --models glm,qwen,minimax
```

If model selection isn't supported, OpenCode uses its default model roster.

## Prompt Construction

Request multi-model perspectives explicitly:

```
You are reviewing the following. Please gather perspectives from multiple
model families if available:

SCOPE: {review_scope}
CONTEXT: {context_summary}
DOMAINS: {domains}
INTENSITY: {intensity}

For each domain, identify issues. If you have access to multiple models,
report which model surfaced each finding.

Return JSON with findings array and optional model attribution per finding.
```

## Execution

### MCP Path

```
Call MCP OpenCode API with:
  prompt: {constructed_prompt}
  models: ["glm", "qwen", "minimax"]
  timeout: {calculated_timeout}
```

### CLI Path

```bash
timeout {calculated_timeout} opencode run \
  --prompt "{constructed_prompt}" \
  --no-interactive
```

## Output Format

```json
{
  "bridge": "opencode",
  "model_family": "multi-model",
  "models_used": ["glm", "qwen", "minimax"],
  "connection_used": "mcp | cli",
  "review_id": "...",
  "status": "COMPLETED | SKIPPED",
  "skip_reason": "...",
  "domains_covered": [],
  "findings": [
    {
      "id": "OF001",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "...",
      "domain": "...",
      "attributed_model": "glm | qwen | minimax | unknown"
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS | null",
  "timeout_used": 270,
  "confidence": "high | medium | low"
}
```

Note: `attributed_model` field is present when OpenCode returns model-attributed findings. Preserve attribution — it's valuable for cross-model analysis.

## Notes

- OpenCode is the widest-coverage single bridge (multi-model internally)
- Always apply 1.5× timeout multiplier for multi-model overhead
- Preserve model attribution in findings when available
- SKIPPED is a valid non-error outcome
- Never block the orchestrator — always return a report
