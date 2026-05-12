# Claude Code CLI Reference

Complete reference for `claude` CLI non-interactive usage. Used when runtime-claude runs via an external executor (OpenCode, Codex, Gemini, or any agent that can shell out to `claude`).

---

## Non-Interactive Mode

```bash
claude -p "prompt"
```

The `-p` flag runs Claude non-interactively without opening an interactive session.

---

## Key Flags

| Flag | Values | Purpose |
|------|--------|---------|
| `-p`, `--print` | string | Prompt string — enables non-interactive mode |
| `--output-format` | `text`, `json`, `stream-json` | Output format |
| `--permission-mode` | see table below | Controls what actions Claude can take |
| `--effort` | `low`, `medium`, `high`, `xhigh`, `max` | Thinking/reasoning depth |
| `--allowedTools` | space-separated tool names | Allow specific tools (e.g. `"Read Grep Glob"`) |
| `--disallowedTools` | space-separated tool names | Deny specific tools |
| `--tools` | space-separated tool names | Specify the exact set of available tools |
| `--bare` | — | Minimal mode: no hooks, LSP, plugins, CLAUDE.md auto-discovery |
| `--model` | model ID or alias | Override model (`sonnet`, `opus`, `haiku`, or full ID) |
| `--agents` | JSON string | Define custom inline agents |
| `--agent` | agent name | Use a specific configured agent for the session |
| `--append-system-prompt` | string | Append additional system prompt |
| `--system-prompt` | string | Override the default system prompt entirely |
| `--max-budget-usd` | float | Cap total API spend (only with `--print`) |
| `--session-id` | UUID | Use a specific session ID |
| `-c`, `--continue` | — | Resume most recent session |
| `--resume` | session ID | Resume a specific session |
| `--verbose` | — | Debug output (remove in production) |
| `--dangerously-skip-permissions` | — | Bypass ALL permission checks (sandboxed env only) |
| `--allow-dangerously-skip-permissions` | — | Enable bypass as an option without it being default |

---

## Permission Modes

`--permission-mode` is the primary way to control capability profile from external executors:

| Mode | Behavior | Bridge use |
|------|----------|-----------|
| `default` | Prompts user on each tool call | Unusable for automated dispatch |
| `acceptEdits` | Auto-accepts file edits; prompts for Bash | Inspect tasks with file reads |
| `auto` | Auto-accepts everything except unsafe Bash | Standard automated use |
| `bypassPermissions` | Skips all checks (like `--dangerously-skip-permissions`) | Trusted sandboxed env only |
| `dontAsk` | Never prompts; rejects instead of asking | Strict non-interactive mode |
| `plan` | Shows plan before executing; requires approval | Not suitable for automated dispatch |

**Recommended bridge mappings:**

| capability_profile | Recommended `--permission-mode` |
|-------------------|-------------------------------|
| `inspect` | `acceptEdits` (reads freely; edits require no prompt since we only read) |
| `modify` | `auto` (auto-accepts edits and safe Bash) |

For tightly controlled inspect tasks, combine with `--allowedTools`:
```bash
--permission-mode acceptEdits --allowedTools "Read Grep Glob Bash(ls *) Bash(cat *)"
```

---

## Effort Levels

`--effort` maps directly to bridge intensity. Use this instead of relying on prompt-level instructions for reasoning depth:

| bridge `intensity` | `--effort` value |
|-------------------|-----------------|
| `quick` | `low` |
| `standard` | `medium` |
| `thorough` | `high` |
| n/a (security/compliance) | `xhigh` |

---

## Bare Mode (Recommended for Bridge Use)

`--bare` minimizes overhead by disabling hooks, LSP, plugin sync, CLAUDE.md auto-discovery, and background prefetches. Ideal for bridge dispatch from external executors where you control all context explicitly:

```bash
claude -p "{prompt}" \
  --bare \
  --output-format json \
  --permission-mode acceptEdits \
  --effort medium
```

In bare mode, provide context explicitly via `--system-prompt`, `--append-system-prompt`, or `--add-dir`.

---

## Output Formats

| Format | Description | Use Case |
|--------|-------------|---------|
| `text` | Plain text (default) | Human-readable output |
| `json` | Structured JSON result | Programmatic parsing |
| `stream-json` | Streaming JSON events | Real-time processing, long tasks |

---

## Inspect Profile — Read-Only Analysis

```bash
claude -p "{prompt}" \
  --bare \
  --output-format json \
  --permission-mode acceptEdits \
  --allowedTools "Read Grep Glob Bash(ls *) Bash(find *) Bash(cat *)" \
  --effort medium
```

---

## Modify Profile — Implementation Tasks

```bash
claude -p "{prompt}" \
  --bare \
  --output-format json \
  --permission-mode auto \
  --effort medium
```

---

## Inline Agent Definition

Define custom domain expert agents without a `.claude/agents/` directory:

```bash
claude -p "{prompt}" \
  --bare \
  --output-format json \
  --agents '{"security-expert": {"description": "Security vulnerability reviewer", "prompt": "You are a security engineer. Review for injection vulnerabilities, auth flaws, secrets in code, and insecure data handling."}}'
```

---

## Piping Input

```bash
# Pipe file contents as context
cat error.log | claude -p "Analyze this log for errors"

# Pipe from another command
git diff | claude -p "Summarize what changed"
```

---

## Agent Teams (Claude Code native, not CLI-invocable)

Agent Teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in environment and are only available when Claude Code is the executor. They cannot be triggered via `claude -p`.

Enable in `settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

---

## Sub-Agents (Custom)

Define specialized sub-agents in `.claude/agents/`:

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a security engineer. Review for injection vulnerabilities,
auth flaws, secrets in code, and insecure data handling.
```

Invoke: `"Use a security-reviewer subagent to analyze src/auth/"`

---

## Anthropic API (Fallback)

When `claude` CLI is not available, fall back to the Anthropic API directly:

```bash
# Discover latest model at runtime
CLAUDE_MODEL=$(curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/models \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])")

curl -s -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$CLAUDE_MODEL\",
    \"max_tokens\": 8096,
    \"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}]
  }"
```

---

## Installation

```bash
# Via npm
npm install -g @anthropic-ai/claude-code

# Check version
claude --version
```
