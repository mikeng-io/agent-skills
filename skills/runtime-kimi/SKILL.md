---
name: runtime-kimi
description: Reference adapter for Kimi Code CLI dispatch. Read by any orchestrating skill via the Read tool. Defines how to invoke Kimi CLI in non-interactive mode, timeout estimation, and fallback behavior. Usable by deep-council, deep-review, deep-audit, or any future skill that needs Kimi-based review.
location: managed
context: reference
dependencies:
  - runtime-contracts
  - domain-registry
---

# Bridge: Kimi Code Adapter

This file is a REFERENCE DOCUMENT. Any orchestrating skill reads it via the `Read` tool and embeds its instructions directly into Task agent prompts. It is not invoked as a standalone skill — it is a reusable set of instructions for Kimi CLI dispatch.

**Input schema, agent prompt template, output schema, verdict logic, timeout formula, artifact format, and status semantics are defined in `runtime-contracts/SKILL.md`. This file covers only Kimi-specific connection detection and execution.**

## Bridge Identity

```yaml
bridge: kimi
model_family: moonshot/kimi
availability: conditional
connection_preference:
  1: native-dispatch # Executor is Kimi CLI — kimi native subagents (coder/explore/plan)
  2: mcp # Any executor with kimi-code-mcp configured — mcp__kimi__* tools
  3: cli # Any other executor — kimi --print -p --afk
  4: skip # None available — return SKIPPED (non-blocking)

native_dispatch:
  detection: "Running inside Kimi CLI session AND kimi agent tool is accessible"
  reliability: "MEDIUM — context awareness + tool availability"
  subagent_types: ["coder", "explore", "plan"]

mcp:
  package: "kimi-code-mcp"
  install: "npm install -g kimi-code-mcp"
  config_key: "kimi"
  requires: "kimi CLI installed and authenticated; KIMI_CLI_PATH if not on PATH"
```

---

## Pre-Flight — Connection Detection

**MUST read `runtime-contracts/tool-discovery.md` first** to understand the discovery protocol.

### Step 1.0: Discover Execution Context

Before checking connection paths, discover what dispatch methods are available in the CURRENT execution context.

**Primary detection: Native subagent tool availability**

```yaml
kimi_native:
  signal: "kimi Agent tool is accessible with subagent_type parameter"
  check: "Can invoke Agent with subagent_type in ['coder', 'explore', 'plan']"
  reliability: MEDIUM (requires tool availability check)
```

**If running INSIDE Kimi CLI with native subagents**:

```json
{
  "executor_type": "kimi",
  "native_dispatch": {
    "available": true,
    "subagent_types": ["coder", "explore", "plan"],
    "session_continuity": true
  },
  "recommended_dispatch": "native"
}
```

→ **Use native dispatch** (Step 3A). This allows Kimi to spawn typed subagents in parallel.

**If NOT running inside Kimi CLI**, proceed to Check A.

---

### Check A: MCP Server Configured?

Look for a `kimi` entry in the active MCP configuration:

```bash
cat .mcp.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'kimi' in d.get('mcpServers',{}) else 'not-found')" 2>/dev/null
cat ~/.claude.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('found' if 'kimi' in str(d) else 'not-found')" 2>/dev/null
```

If found → **use MCP path** (Step 3B). No further pre-flight needed — MCP server handles auth internally.

If not found → proceed to Check B.

---

### Check B: CLI Installed?

```bash
which kimi
```

If found → proceed to Check C.

If not found → **return SKIPPED** (non-blocking).

```json
{
  "bridge": "kimi",
  "status": "SKIPPED",
  "skip_reason": "kimi CLI not found — install via: curl -LsSf https://code.kimi.com/install.sh | bash",
  "outputs": []
}
```

---

### Check C: Authenticated?

```bash
# Check for API key (headless/CI path — no interactive auth needed)
echo ${KIMI_API_KEY:+found}

# Or check if previous login session exists
kimi info 2>/dev/null | grep -q "kimi-cli version" && echo "cli_available"
```

If `KIMI_API_KEY` is set → authenticated for headless use. Proceed to Step 2.

If no API key but `kimi info` works (OAuth session may exist) → proceed to Step 2, but note that non-interactive dispatch requires `--afk`.

If neither → return `HALTED` with advisory:

```
⚠ Kimi CLI found but no authentication configured.

Options:
  [1] Set KIMI_API_KEY environment variable
      export KIMI_API_KEY="sk-..."
      Then re-run this review.

  [2] Login interactively
      kimi login     # Opens browser OAuth flow

  [3] Skip Kimi bridge and continue
  [4] Abort the entire review
```

---

## Step 2: Select Dispatch Mode

```yaml
dispatch_mode:
  native_subagents:
    condition: "Running inside Kimi CLI AND Agent tool accessible"
    description: "Spawn typed subagents (coder/explore/plan) in parallel"
    preferred: true

  mcp:
    condition: "kimi MCP server configured in .mcp.json or executor MCP config"
    description: "Invoke kimi-code-mcp tools — no CLI overhead, persistent sessions"
    preferred: false (second choice after native)

  cli_print:
    condition: "Default CLI fallback — kimi found and authenticated, no MCP"
    description: "kimi --print -p invocation with --afk for fully headless use"
    preferred: false
```

---

## Step 3A: Execute via Native Subagents (preferred when inside Kimi)

When running as the Kimi executor with native subagent access, spawn typed sub-agents in parallel:

```
Subagent 1: {domain_1} expert — subagent_type: explore (for inspect tasks)
Subagent 2: {domain_2} expert — subagent_type: explore (for inspect tasks)
...
Subagent N: Integration Checker — subagent_type: explore
```

For `implement` tasks, use `subagent_type: coder` instead of `explore`.

**Subagent type mapping:**

| capability_profile | subagent_type |
|--------------------|---------------|
| `inspect` | `explore` |
| `modify` | `coder` |

**Important constraint:** Kimi subagents cannot spawn further subagents (no recursion). Keep the dispatch flat — one parent, N typed subagents.

After all subagents complete, run the runtime-contracts Post-Analysis Protocol inline (parent agent holds all state).

---

## Step 3B: Execute via MCP (kimi-code-mcp)

When `kimi-code-mcp` is configured as an MCP server, invoke it directly. This avoids CLI subprocess overhead and supports persistent sessions.

**Setup** (if not already configured — offer as auto-setup option):

```json
{
  "mcpServers": {
    "kimi": {
      "command": "kimi-code-mcp",
      "env": {
        "KIMI_CLI_PATH": "/path/to/kimi"
      }
    }
  }
}
```

**Invocation:** Use `mcp__kimi__*` tools as available in the executor's MCP toolset. Prompt construction follows the same Agent Prompt Template from runtime-contracts.

If MCP invocation fails → fall back to Step 3C (CLI).

---

## Step 3C: Execute via CLI (external executors)

When any non-Kimi executor can call the `kimi` CLI:

```bash
# Resolve from runtime-contracts capability_profile + runtime_input.intensity
# inspect → --thinking (default)
# thorough → --thinking (force on)
# quick    → --no-thinking

timeout {final_timeout} kimi \
  --print \
  -p "{constructed_prompt}" \
  --afk \
  --output-format stream-json \
  --thinking \
  {model_flag}
```

**Key flags:**

| Flag | Purpose |
|------|---------|
| `--print` | Non-interactive mode (required for automated dispatch) |
| `-p "prompt"` | Prompt string |
| `--afk` | Auto-approve all tool calls and dismiss questions — required for headless use |
| `--yolo / -y` | Auto-approve all tool calls (use `--afk` instead — it also handles questions) |
| `--output-format stream-json` | Structured JSONL output for parsing |
| `--thinking` | Enable extended thinking (better for thorough intensity) |
| `--no-thinking` | Disable thinking (use for quick intensity) |
| `--model NAME` | Override model (omit to use configured default) |
| `--session/-r` | Resume a session by ID |
| `--continue/-C` | Continue most recent session |
| `--mcp-config FILE` | Load additional MCP configs |

**Intensity → thinking mapping:**

| bridge `intensity` | `--thinking` flag |
|--------------------|------------------|
| `quick` | `--no-thinking` |
| `standard` | `--thinking` (default) |
| `thorough` | `--thinking` |

**Model selection:** Do not hardcode. If `.runtime-settings.json` specifies `model` for the kimi bridge, pass as `--model {model}`. Otherwise, omit the flag and use the configured default from `~/.kimi/config.toml`.

For the Post-Analysis Protocol rounds, use separate `kimi --print` calls — no cross-call session state. Embed the full previous-round context in each Round N prompt (stateless pattern, same as Gemini CLI).

---

## Output Parsing

Kimi `--output-format stream-json` emits JSONL events. Parse the final message from the stream:

```bash
# Capture JSONL stream, extract final assistant message
kimi --print -p "..." --afk --output-format stream-json 2>/dev/null | \
  python3 -c "
import sys, json
events = [json.loads(l) for l in sys.stdin if l.strip()]
# Find last assistant message content
for ev in reversed(events):
  if ev.get('type') == 'message' and ev.get('role') == 'assistant':
    print(json.dumps(ev.get('content', '')))
    break
"
```

If `--output-format stream-json` is not available or fails, fall back to `--output-format text` and attempt to extract JSON from the text response.

---

## CLI Error Handling

| Exit code | Meaning | Action |
|-----------|---------|--------|
| `0` | Success | Parse stream output |
| `1` | Permanent failure (auth, config, quota) | Return `SKIPPED`, capture stderr |
| `75` | Transient / retryable (rate limit, timeout, server error) | Return `SKIPPED`, reason: `transient_error_exit_75` |
| `124` | Timeout (from `timeout` wrapper) | Return `SKIPPED`, reason: `timeout_after_{n}s` |
| Other non-zero | CLI error | Capture stderr; return `SKIPPED` with detail |

---

## Timeout Estimation

Use runtime-contracts base timeout table. Apply a 1.3× multiplier for subagent spawn overhead when running natively inside Kimi.

No additional multiplier for CLI path.

---

## Output

See runtime-contracts Output Schema. Bridge-specific fields:

```json
{
  "bridge": "kimi",
  "capability_profile": "inspect | modify",
  "model_family": "moonshot/kimi",
  "connection_used": "native-dispatch | cli",
  "thinking_enabled": true
}
```

Output ID prefix: `K` (e.g., `K001`, `K002`).

---

## Notes

- **`--afk` is required for headless dispatch** — without it, Kimi prompts for approval and blocks
- **`--print` enables non-interactive mode** — analogous to `claude -p`
- **Subagent types are typed** — `explore` = read-only, `coder` = read-write, `plan` = planning-only; always map from capability_profile
- **No subagent recursion** — Kimi subagents cannot spawn further subagents; keep dispatch flat
- **API key for CI** — set `KIMI_API_KEY` env var; no interactive login needed in automated pipelines
- **Model selection** — Kimi supports multiple Moonshot models and OpenAI-compatible providers; use `runtime-settings.json` to configure, never hardcode
- **SKIPPED is non-blocking** — if unavailable, other bridges continue
