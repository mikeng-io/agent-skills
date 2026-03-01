---
name: bridge-opencode
description: Reference adapter for OpenCode — model-agnostic multi-provider bridge. Read by any orchestrating skill via the Read tool. Covers pre-flight checks with interactive advisory, HTTP API server path (preferred), CLI run path as fallback, correct flags and model format embedded. Usable by deep-council, deep-review, deep-audit, or any future skill that needs multi-model review.
location: managed
context: reference
---

# Bridge: OpenCode Multi-Model Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for OpenCode dispatch.

## Bridge Identity

```yaml
bridge: opencode
model_family: multi-provider   # Routes to any configured AI provider
availability: conditional
connection_preference:
  1: http-api    # opencode serve — persistent server, REST API at :4096
  2: cli         # opencode run "prompt" — non-interactive single-shot
  3: halt        # Neither: surface advisory, offer setup
```

## Why OpenCode?

OpenCode is provider-agnostic — it routes to whichever AI providers are configured (Anthropic, OpenAI, Google, GLM, Qwen, etc.). Running it as a bridge lets the calling skill get a second opinion from a different model family than the one currently executing the skill.

**Trade-off:** 1.5× timeout multiplier applies because model calls go through OpenCode's routing layer.

---

## Step 1: Pre-Flight — Connection Detection

### Check A: HTTP API Server Running?

```bash
curl -s --max-time 3 http://localhost:4096 -o /dev/null -w "%{http_code}"
# Also check custom port if OPENCODE_PORT env var is set
```

If responds (any HTTP code) → **use HTTP API path** (Step 3A). Server is already running.

---

### Check B: CLI Installed?

```bash
which opencode
```

If found → proceed to Check C.

If not found → **no connection available — go to Step 2 (Advisory)**.

---

### Check C: Provider Authenticated? (CLI path only)

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

## Step 3: Input Format

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

---

## Step 4: Build Prompt

```
You are a multi-domain reviewer. Analyze the following for issues across
the specified domains. For each domain, act as the corresponding domain expert.

Review scope: {review_scope}
Context: {context_summary}
Intensity: {intensity}

Domains to review:
{for each domain:
  "- {domain_name}: {focus areas from domain-registry}"}

Return findings as JSON:
{
  "domains_analyzed": [...],
  "findings": [
    {
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "...",
      "domain": "..."
    }
  ],
  "verdict": "PASS | FAIL | CONCERNS"
}
```

---

## Step 5: Timeout Estimation

OpenCode routes through its provider layer — apply 1.5× multiplier:

```yaml
scope_under_5_files_or_500_loc:    base_timeout: 60
scope_5_to_20_files_or_2000_loc:   base_timeout: 180
scope_20_to_50_files_or_10k_loc:   base_timeout: 300
scope_50_plus_files_or_10k_plus:   base_timeout: 600

opencode_multiplier: 1.5   # Always applied — provider routing overhead

intensity_multiplier:
  quick: 0.5
  standard: 1.0
  thorough: 1.5

final_timeout: base_timeout * 1.5 * intensity_multiplier   # seconds
```

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

# Send prompt
curl -s -X POST http://localhost:4096/session/$SESSION/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": [{"type": "text", "text": "{constructed_prompt}"}],
    "model": "{provider/model}"
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

```bash
timeout {final_timeout} opencode run "{constructed_prompt}" \
  --format json \
  --model {provider/model}
```

See `cli-reference.md` for complete flag reference.

**Important:** `opencode` (bare) opens the interactive TUI. Always use `opencode run "..."` for programmatic use.

### CLI Error Handling

| Exit code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Parse JSON event stream for final message |
| 124 | Timeout | Return SKIPPED, `skip_reason: timeout_after_{n}s` |
| Other | CLI error | Capture stderr, return SKIPPED with detail |

---

## Step 6: Output Format

```json
{
  "bridge": "opencode",
  "model_family": "multi-provider",
  "model_used": "provider/model or null",
  "connection_used": "http-api | cli",
  "session_id": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "status": "COMPLETED | SKIPPED | HALTED | ABORTED",
  "halt_reason": "cli_not_found | no_provider_configured | null",
  "halt_message": "Advisory text for caller to surface to user",
  "skip_reason": "...",
  "domains_covered": [],
  "outputs": [
    {
      "id": "O001",
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
  "timeout_used": 270,
  "confidence": "high | medium | low"
}
```

### Status Semantics (orchestrators must handle all four):

| Status | Meaning | Orchestrator action |
|--------|---------|---------------------|
| `COMPLETED` | Review ran, findings returned | Include in synthesis |
| `SKIPPED` | Non-fatal error (timeout, parse failure) | Note in report, continue |
| `HALTED` | Pre-flight failed — needs user input | Surface `halt_message`, wait |
| `ABORTED` | User chose to abort | Stop the orchestrator |

---

## Notes

- **HTTP API is preferred** — use it when `opencode serve` is already running (lower overhead, session continuity)
- **`opencode run` ≠ `opencode`** — bare `opencode` opens the interactive TUI; always use `opencode run "..."` for scripted use
- **Model format is `provider/model`** — e.g., `anthropic/claude-sonnet-4-20250514`, not just `claude`
- **`plan` agent** is the safe choice for review tasks (read-only mode)
- **1.5× timeout multiplier** always applies (provider routing overhead)
- **HALTED ≠ SKIPPED** — HALTED requires user input before the review can proceed
