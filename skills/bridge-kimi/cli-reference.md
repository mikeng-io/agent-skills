# Kimi Code CLI Reference

Complete reference for `kimi` CLI non-interactive usage. Used when bridge-kimi runs via an external executor (Claude Code, OpenCode, Codex, Gemini, or any agent that can shell out to `kimi`).

---

## Non-Interactive Mode

```bash
kimi --print -p "prompt" --afk
```

`--print` enables non-interactive mode. `--afk` auto-approves all tool calls and dismisses questions — required for fully headless dispatch.

---

## Key Flags

| Flag | Values | Purpose |
|------|--------|---------|
| `--print` | — | Non-interactive mode (required for bridge dispatch) |
| `-p`, `--prompt` | string | Prompt string |
| `-c`, `--command` | string | Alias for `--prompt` |
| `--afk` | — | Auto-approve tools AND dismiss questions — use for bridge dispatch |
| `-y`, `--yolo`, `--yes` | — | Auto-approve tool calls only (use `--afk` — it also handles questions) |
| `--output-format` | `text`, `stream-json` | Output format; prefer `stream-json` for structured parsing |
| `--thinking` / `--no-thinking` | — | Enable/disable extended thinking (maps to intensity) |
| `--model` / `-m` | model name | Override model |
| `--quiet` | — | Shorthand for `--print --output-format text --final-message-only` |
| `--final-message-only` | — | Suppress intermediate output |
| `--session` / `--resume` / `-r` | session ID | Resume a session by ID |
| `--continue` / `-C` | — | Continue most recent session in working dir |
| `--config` | TOML/JSON string | Inline config override |
| `--config-file` | file path | Config file (default: `~/.kimi/config.toml`) |
| `--mcp-config-file` | file path | Additional MCP config to load |
| `--mcp-config` | JSON string | Inline MCP config |
| `--agent-file` | file path | Custom agent YAML spec |
| `--add-dir` | directory | Expand workspace scope |
| `--work-dir` / `-w` | directory | Set working directory |
| `--max-steps-per-turn` | integer | Cap steps per turn |

---

## Exit Codes

| Code | Meaning | Bridge action |
|------|---------|---------------|
| `0` | Success | Parse output |
| `1` | Permanent failure (auth, config, quota) | Return `SKIPPED`, log stderr |
| `75` | Transient / retryable (rate limit, server error) | Return `SKIPPED`, reason: `transient_exit_75` |
| `124` | Timeout from `timeout` wrapper | Return `SKIPPED`, reason: `timeout_after_{n}s` |

---

## Intensity → Thinking Mapping

| bridge `intensity` | `--thinking` flag |
|--------------------|------------------|
| `quick` | `--no-thinking` |
| `standard` | *(omit — use configured default)* |
| `thorough` | `--thinking` |

---

## Inspect Profile — Read-Only Analysis

```bash
kimi \
  --print \
  -p "{prompt}" \
  --afk \
  --output-format stream-json \
  --no-thinking
```

For thorough inspect tasks, add `--thinking`.

---

## Modify Profile — Implementation Tasks

```bash
kimi \
  --print \
  -p "{prompt}" \
  --afk \
  --output-format stream-json \
  --thinking
```

---

## Output Parsing (stream-json)

`--output-format stream-json` emits JSONL events. Extract the final assistant message:

```bash
kimi --print -p "..." --afk --output-format stream-json 2>/dev/null | \
  python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
        # Kimi stream-json: look for type=message, role=assistant
        if ev.get('type') == 'message' and ev.get('role') == 'assistant':
            last = ev
    except:
        pass
if last:
    print(json.dumps(last.get('content', '')))
"
```

If `stream-json` fails, fall back to `--output-format text` and attempt JSON extraction from the text response.

---

## Authentication

**Headless / CI (recommended for bridge use):**
```bash
export KIMI_API_KEY="sk-..."   # Moonshot API key — overrides config file
```

**OAuth (interactive login):**
```bash
kimi login     # browser OAuth flow
```

Config file: `~/.kimi/config.toml`

```toml
[providers.moonshot-cn]
type = "kimi"
base_url = "https://api.moonshot.cn/v1"
api_key = "sk-..."
```

---

## MCP Server (kimi-code-mcp)

Kimi CLI can be exposed as an MCP server via the `kimi-code-mcp` npm package, allowing external executors to invoke it over MCP without shelling out:

```bash
npm install -g kimi-code-mcp
```

Requires `KIMI_CLI_PATH` env var if `kimi` is not on PATH.

Add to `.mcp.json`:
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

---

## Subagent Types (Native Dispatch — inside Kimi only)

| Type | Access | Use for |
|------|--------|---------|
| `coder` | Read + write + shell | Implementation tasks (`modify` capability profile) |
| `explore` | Read-only | Analysis, review, research (`inspect` capability profile) |
| `plan` | Read-only, no shell | Planning, architecture design |

Subagents cannot spawn further subagents (no recursion). Keep dispatch flat.

---

## Installation

```bash
# Primary (recommended)
curl -LsSf https://code.kimi.com/install.sh | bash

# pip
pip install kimi-cli

# Verify
kimi --version
kimi info
```
