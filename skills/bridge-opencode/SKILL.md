---
name: bridge-opencode
description: Reference adapter for OpenCode — model-agnostic multi-provider bridge. Read by any orchestrating skill via the Read tool. Covers pre-flight checks with interactive advisory, HTTP API server path (preferred), CLI run path as fallback, correct flags and model format embedded. Usable by deep-council, deep-review, deep-audit, or any future skill that needs multi-model review.
location: managed
context: reference
---

# Bridge: OpenCode Multi-Model Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for OpenCode dispatch.

**Input schema, agent prompt template, output schema, verdict logic, artifact format, and status semantics are defined in `bridge-commons/SKILL.md`. This file covers OpenCode-specific connection detection, timeout multiplier, and execution paths.**

## Bridge Identity

```yaml
bridge: opencode
model_family: multi-provider   # Routes to any configured AI provider
availability: conditional
connection_preference:
  1: native-dispatch  # Executor is OpenCode — internal agent routing
  2: http-api         # Any executor — opencode serve REST API at :4096
  3: cli              # Any other executor — opencode run
  4: halt             # None available — surface advisory, offer setup
```

## Why OpenCode?

OpenCode is provider-agnostic — it routes to whichever AI providers are configured (Anthropic, OpenAI, Google, GLM, Qwen, etc.). Running it as a bridge lets the calling skill get a second opinion from a different model family than the one currently executing the skill.

**Trade-off:** 1.5× timeout multiplier applies because model calls go through OpenCode's routing layer.

---

## Step 1: Pre-Flight — Connection Detection

### Check A: Native Dispatch?

If the executor is OpenCode, this is the preferred path — route the task to an OpenCode internal agent within the current session rather than shelling out or calling the HTTP API.

```bash
# Check if running inside an OpenCode session
echo ${OPENCODE_SESSION_ID:+found}
# Alternatively: OPENCODE_CLIENT is set when OpenCode is the executor
echo ${OPENCODE_CLIENT:+found}
```

If in an OpenCode session → **use native dispatch** (route to `general` or `explore` subagent).

If executor is not OpenCode → proceed to Check B.

---

### Check B: HTTP API Server Running?

```bash
curl -s --max-time 3 http://localhost:4096 -o /dev/null -w "%{http_code}"
# Also check custom port if OPENCODE_PORT env var is set
```

If responds (any HTTP code) → **use HTTP API path** (Step 3A). Server is already running.

---

### Check C: CLI Installed?

```bash
which opencode
```

If found → proceed to Check D.

If not found → **no connection available — go to Step 2 (Advisory)**.

---

### Check D: Provider Authenticated? (CLI path only)

```bash
opencode auth list
```

If output shows at least one authenticated provider → proceed to CLI path.

If no providers configured → **go to Step 2 (Advisory)** with `reason: no_provider_configured`.

---

## Step 2: Advisory — Halt and Present Options

**Do not skip silently.** Surface the appropriate message and wait for a choice.

### Advisory: Not Installed

```
⚠ OpenCode is not installed or not in PATH.

Options:
  [1] Install OpenCode
      npm install -g opencode-ai
      # or: brew install opencode

  [2] Start the OpenCode server (if already installed elsewhere)
      opencode serve --port 4096
      Then re-run this review.

  [3] Skip OpenCode bridge
      Continue without OpenCode. Other available bridges will run.

  [4] Abort the entire review

What would you like to do? (1/2/3/4)
```

Return `status: HALTED`, `halt_reason: cli_not_found`.

---

### Advisory: No Provider Configured

```
⚠ OpenCode is installed but no AI provider is authenticated.

Configure a provider:
  opencode auth login    # Select and authenticate a provider

Alternatively:
  [1] Skip OpenCode bridge
  [2] Abort the entire review
```

Return `status: HALTED`, `halt_reason: no_provider_configured`.

---

### Non-Interactive Environments

Return `status: HALTED` with the full advisory in `halt_message`. Never silently skip.

---

## Timeout Estimation

Use bridge-commons base timeout table and intensity multiplier, then apply the OpenCode-specific multiplier:

```yaml
opencode_multiplier: 1.5   # Always applied — provider routing overhead

final_timeout: base_timeout × intensity_multiplier × 1.5   # seconds
```

OpenCode internally dispatches to one or more providers — each provider call adds latency.

---

## Step 3A: Execute via HTTP API (Preferred)

The OpenCode HTTP server exposes a REST API. Use it when the server is already running.

OpenAPI spec available at: `http://localhost:{port}/doc`

### Create a session and send a message

```bash
# Create session
SESSION=$(curl -s -X POST http://localhost:4096/session \
  -H "Content-Type: application/json" \
  -d '{"title": "bridge-review-{review_id}"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Send prompt — use bridge-commons Agent Prompt Template for the constructed_prompt
curl -s -X POST http://localhost:4096/session/$SESSION/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": [{"type": "text", "text": "{constructed_prompt}"}],
    "model": "{provider/model}"
  }'
```

After the initial response, send the consolidation pass as a second message:

```bash
curl -s -X POST http://localhost:4096/session/$SESSION/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": [{"type": "text", "text": "Review and consolidate the findings above. Identify conflicts, gaps, and cross-domain issues. Add any new findings with domain: cross-domain."}]
  }'
```

### Model format

Models must use `provider/model` format:

```yaml
model_format: "provider/model"
examples:
  - "anthropic/claude-sonnet-4-20250514"
  - "openai/gpt-4o"
  - "google/gemini-2.0-flash"
  - "glm/glm-4-flash"          # If GLM configured
  - "qwen/qwen-plus"           # If Qwen configured

selection_strategy:
  - Use default model if no preference (omit model field)
  - Or pass the model configured in the caller's context
```

### Authentication (if server has password)

```bash
# With auth: -u opencode:$OPENCODE_SERVER_PASSWORD
curl -s -u opencode:$OPENCODE_SERVER_PASSWORD \
  -X POST http://localhost:4096/session/...
```

### Agent selection (optional)

```bash
# Use the built-in 'plan' agent for read-only analysis
curl -s -X POST http://localhost:4096/session \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "agent": "plan"}'
```

Built-in agents:
- `plan` — restricted, read-only, suited for analysis tasks
- `build` — full tool access (not appropriate for review-only)

---

## Step 3B: Execute via CLI (Fallback)

Build the prompt using the bridge-commons Agent Prompt Template.

```bash
timeout {final_timeout} opencode run "{constructed_prompt}" \
  --format json \
  --model {provider/model}
```

**Important:** `opencode` (bare) opens the interactive TUI. Always use `opencode run "..."` for programmatic use.

### CLI Error Handling

| Exit code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Parse JSON event stream for final message |
| 124 | Timeout | Return SKIPPED, `skip_reason: timeout_after_{n}s` |
| Other | CLI error | Capture stderr, return SKIPPED with detail |

---

## Output

See bridge-commons Output Schema. Bridge-specific fields:

```json
{
  "bridge": "opencode",
  "model_family": "multi-provider",
  "connection_used": "native-dispatch | http-api | cli",
  "model_used": "provider/model or null"
}
```

Output ID prefix: `O` (e.g., `O001`, `O002`).

---

## Notes

- **HTTP API is preferred** — use it when `opencode serve` is already running (lower overhead, session continuity)
- **`opencode run` ≠ `opencode`** — bare `opencode` opens the interactive TUI; always use `opencode run "..."` for scripted use
- **Model format is `provider/model`** — e.g., `anthropic/claude-sonnet-4-20250514`, not just `claude`
- **`plan` agent** is the safe choice for review tasks (read-only mode)
- **1.5× timeout multiplier** always applies (provider routing overhead)
- **HALTED ≠ SKIPPED** — HALTED requires user input before the review can proceed
