---
name: bridge-codex
description: Reference adapter for Codex multi-agent review. Read by any orchestrating skill via the Read tool. MCP server path (preferred) with auto-setup option, CLI path as fallback, interactive pre-flight advisory when not configured, correct flags embedded. Usable by deep-council, deep-review, deep-audit, or any future skill that needs Codex-based review.
location: managed
context: reference
---

# Bridge: Codex Multi-Agent Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Codex review dispatch via MCP server or CLI.

## Bridge Identity

```yaml
bridge: codex
model_family: openai/codex
connection_preference:
  1: mcp-server    # codex mcp-server — preferred: persistent, no auth check needed
  2: cli           # codex exec — direct CLI, requires auth + feature flag
  3: halt          # Neither available: surface advisory, offer setup
multi_agent: required        # Must be enabled for parallel domain dispatch
availability: conditional
```

---

## Step 1: Pre-Flight — Connection Detection

### Check A: MCP Server Configured?

Look for a `codex` entry in the active MCP configuration:

```bash
# Check project-level MCP config
cat .mcp.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'codex' in d.get('mcpServers',{}) else 'not-found')" 2>/dev/null

# Or check Claude's global MCP settings
cat ~/.claude.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'codex' in str(d) else 'not-found')" 2>/dev/null
```

If found → **use MCP path** (Step 3A). No further pre-flight needed — MCP server handles auth internally.

---

### Check B: CLI Available?

```bash
which codex
```

If found → proceed to Check C.

If not found → **no connection available — go to Step 2 (Advisory)**.

---

### Check C: Authenticated? (CLI path only)

```bash
codex login status
```

Exit code 0 → authenticated. Other → **go to Step 2 (Advisory)** with `reason: not_authenticated`.

---

### Check D: Multi-Agent Feature Enabled? (CLI path only — optional)

```bash
codex features list
```

Look for `multi_agent` marked as enabled.

- If enabled → proceed with **parallel multi-agent dispatch** (one sub-agent per domain)
- If not enabled → proceed in **single-agent mode** (one Codex session reviews all domains together)

Multi-agent is a progressive enhancement. Single-agent mode is a valid fallback — do not halt.

Record `multi_agent_enabled: true/false` in output for caller transparency.

→ **Use CLI path** (Step 3B).

---

## Step 2: Advisory — Halt and Present Options

**Do not skip silently.** Surface the appropriate message to the user and wait for a choice.

### Advisory: MCP Server Not Configured + CLI Not Found

```
⚠ Codex is not connected. This bridge requires either the Codex MCP server
  or the Codex CLI.

Options:
  [1] Set up MCP server automatically
      I will add the Codex MCP server to .mcp.json so future sessions
      use it without any CLI installation needed.
      Requires: Node.js 18+ and npx available.

  [2] Install the Codex CLI
      Run: npm install -g @openai/codex
      Then re-run this review.

  [3] Skip Codex bridge
      Continue the review without Codex. Other available bridges will run.

  [4] Abort
      Stop the entire review.

What would you like to do? (1/2/3/4)
```

**If user chooses [1] — Auto-setup MCP server:**

Write (or merge) into `.mcp.json`:

```json
{
  "mcpServers": {
    "codex": {
      "command": "npx",
      "args": ["-y", "codex", "mcp-server"]
    }
  }
}
```

Then verify the server is reachable. If successful → continue with **MCP path (Step 3A)**.
If verification fails → tell the user and offer options [2]/[3]/[4] again.

**If user chooses [2]:** Return `status: HALTED`, `halt_reason: cli_not_installed`. Show install command.

**If user chooses [3]:** Return `status: SKIPPED`, `skip_reason: user_chose_skip`.

**If user chooses [4]:** Return `status: ABORTED`. Calling orchestrator must stop entire review.

---

### Advisory: CLI Found But Not Authenticated

```
⚠ Codex CLI found but not authenticated.

To log in:
  codex login              # Browser OAuth flow (interactive)
  codex login --device-auth   # Device code flow (headless/CI)

After authenticating, re-run this review.

Or:
  [1] Skip Codex bridge and continue
  [2] Abort the entire review
```

Return `status: HALTED`, `halt_reason: not_authenticated`.

---

### Non-Interactive Environments (Automated Pipelines)

If no interactive context is available, return `status: HALTED` with the full advisory text in `halt_message`. Never silently skip in a way that hides a configuration gap.

---

---

## Reasoning Level Selection

Evaluate the review context and select the Codex reasoning level **before** building the prompt. This applies to both MCP and CLI paths.

### Decision Signals

| Signal | Reasoning Level |
|--------|----------------|
| Security audit, cryptographic review, financial compliance | `xhigh` |
| Multi-component architecture, 3+ CRITICAL findings expected, complex dependency chains | `high` |
| Standard code review, single-domain analysis, routine audit | `medium` |

**Evaluate in this order:**
1. If request explicitly mentions "critical", "security", "cryptographic", "financial", "compliance" → `xhigh`
2. If scope covers 20+ files OR 3+ domains with HIGH risk signals → `high`
3. Otherwise → `medium`

### Xhigh Alert (MANDATORY)

When `xhigh` is selected, **alert the user before proceeding**:

```
⚠ Reasoning level: XHIGH
Codex will use maximum reasoning depth for this review.
This increases token usage and may take 2–3× longer than standard.

Continue? (y/n)
```

If user declines → fall back to `high`. Return `reasoning_level: "high"` in output.

### Embedding Reasoning Level

**MCP path (Step 3A):** pass as `reasoning` parameter
**CLI path (Step 3B):** pass as `--config reasoning-effort={level}` (config override)

Store selected level in `reasoning_level` output field.

---

## Step 3: Build Domain Prompt

Translate `bridge_input.domains` into a Codex multi-agent prompt that leverages Codex's native parallel agent spawning:

```
You are a multi-agent code review coordinator. Spawn one agent per domain
below, run them in parallel using your multi-agent capability, wait for all
to complete, then return a consolidated findings JSON.

Review scope: {review_scope}
Context: {context_summary}
Intensity: {intensity}

Domains to analyze (spawn one agent per domain):
{for each domain:
  "- {domain_name}: focus on {focus_areas from domain-registry}"}

Each agent must return:
{
  "domain": "...",
  "findings": [
    {
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "...",
      "description": "...",
      "evidence": "...",
      "remediation": "..."
    }
  ]
}

After all agents complete, consolidate all findings into:
{
  "domains_analyzed": [...],
  "all_findings": [...],
  "verdict": "PASS | FAIL | CONCERNS"
}
```

---

## Step 4: Timeout Estimation

Multi-agent adds spawning overhead on top of base scope:

```yaml
scope_under_5_files_or_500_loc:    base_timeout: 90    # higher base for agent spawn overhead
scope_5_to_20_files_or_2000_loc:   base_timeout: 240
scope_20_to_50_files_or_10k_loc:   base_timeout: 450
scope_50_plus_files_or_10k_plus:   base_timeout: 720

intensity_multiplier:
  quick: 0.5
  standard: 1.0
  thorough: 1.5

final_timeout: base_timeout * intensity_multiplier   # seconds
```

---

## Step 3A: Execute via MCP Server (Preferred)

Use the `codex` MCP tool directly. The MCP server runs `codex mcp-server` and exposes two tools:

### Model Selection — Check Latest at Runtime

Before calling either MCP or CLI, determine the current latest Codex model:

```bash
# Via CLI
codex models list 2>/dev/null | head -5

# Or check MCP server capabilities via OpenCode spec
# If unavailable, omit model field to use server default
```

Do NOT hardcode a model name. If `codex models list` is unavailable, omit the `model` parameter and let the server select its default.

### Tool: `codex` — Start a session

```
Call: mcp__codex__codex
Parameters:
  prompt:          {constructed_prompt}
  approval-policy: "never"                  # No interactive approval prompts
  sandbox:         "read-only"              # Analysis only — no file writes
  model:           {latest from models list, or omit}
  reasoning:       "{medium|high|xhigh}"    # From Reasoning Level Selection
```

Capture `structuredContent.threadId` from response for multi-turn use.

### Tool: `codex-reply` — Continue session (if needed)

```
Call: mcp__codex__codex-reply
Parameters:
  prompt:   "Summarize and consolidate all agent findings into the JSON format specified."
  threadId: {threadId from previous call}
```

See `cli-reference.md` for complete MCP parameter reference.

---

## Step 3B: Execute via CLI (Fallback)

```bash
# Detect latest model first (if CLI supports it)
CODEX_MODEL=$(codex models list 2>/dev/null | awk 'NR==1{print $1}')
MODEL_FLAG=${CODEX_MODEL:+--model $CODEX_MODEL}   # omit flag if empty

timeout {final_timeout} codex exec "{constructed_prompt}" \
  --sandbox read-only \
  --ask-for-approval never \
  --json \
  --output-last-message /tmp/codex-bridge-{review_id}.json \
  --ephemeral \
  --skip-git-repo-check \
  $MODEL_FLAG \
  --config reasoning-effort={medium|high|xhigh}
```

See `cli-reference.md` for complete flag reference.

### CLI Error Handling:

| Exit code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Parse `--output-last-message` file for findings |
| 124 | Timeout (shell) | Return SKIPPED, `skip_reason: timeout_after_{n}s` |
| Other | CLI error | Capture stderr, return SKIPPED with error detail |
| Valid exit, invalid JSON | Parse error | Attempt partial extraction; else SKIPPED |

---

## Step 5: Output Format

```json
{
  "bridge": "codex",
  "model_family": "openai/codex",
  "connection_used": "mcp | cli",
  "session_id": "...",
  "task_type": "review | planning | implementation | analysis | research",
  "status": "COMPLETED | SKIPPED | HALTED | ABORTED",
  "halt_reason": "cli_not_found | not_authenticated | mcp_setup_failed | null",
  "halt_message": "Advisory text for caller to surface to user",
  "skip_reason": "...",
  "domains_covered": [],
  "outputs": [
    {
      "id": "C001",
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
  "timeout_used": 240,
  "multi_agent_enabled": true,
  "reasoning_level": "medium | high | xhigh",
  "confidence": "high | medium | low"
}
```

### Status Semantics (calling orchestrators must handle all four):

| Status | Meaning | Orchestrator action |
|--------|---------|---------------------|
| `COMPLETED` | Review ran, findings returned | Include in synthesis |
| `SKIPPED` | User chose skip, or non-fatal error | Note in report, continue |
| `HALTED` | Pre-flight failed — needs user input | Surface `halt_message`, wait for user |
| `ABORTED` | User chose to abort entire review | Stop the orchestrator |

---

## Notes

- **MCP server is preferred** — no CLI install needed, auth handled internally, persistent sessions via `codex-reply`
- **Auto-setup option** — orchestrator can write `.mcp.json` to enable MCP server without user installing anything
- **`codex exec` ≠ `codex`** — bare `codex` opens an interactive session; always use `codex exec` for programmatic use
- **`--sandbox read-only` + `--ask-for-approval never`** are required for analysis-only mode
- **HALTED ≠ SKIPPED** — HALTED means the user must make a choice before the review can continue
- **Model**: check latest via `codex models list` at runtime; omit to use server default — never hardcode a model name
- **X-high reasoning requires explicit user confirmation** before proceeding — never activate silently
- **Reasoning level persists in output** (`reasoning_level` field) for caller transparency
- Timeout accounts for multi-agent sub-agent spawn overhead
