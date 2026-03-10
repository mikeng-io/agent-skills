# Tool Discovery: Executor Detection and Capability Discovery

This document defines how bridges discover their execution context and available dispatch methods. Every bridge MUST use this discovery protocol before deciding on a dispatch path.

## Why Tool Discovery Matters

Bridges are executor-agnostic - they run inside Claude Code, OpenCode, Codex CLI, Gemini CLI, or any future executor. Each executor has different capabilities:

- **Native dispatch**: Spawn sub-agents directly (Task tool, `task` tool, etc.)
- **MCP tools**: Access MCP servers like `mcp__codex__codex`
- **CLI tools**: Shell out to command-line tools
- **Session continuity**: Maintain conversation history across rounds

A bridge cannot assume which capabilities are available. It MUST discover them at runtime.

---

## Discovery Protocol

Execute these checks in order. The first successful check determines the dispatch path.

### Step 1: Detect Executor Type

Check environment and tool availability to identify the current executor:

```bash
# Claude Code detection
# Check if Task tool is accessible (not via env var - actual tool check)
# Claude Code exposes: Task, Read, Write, Edit, Bash, Glob, Grep, LSP tools

# OpenCode detection
# Check if lowercase 'task' tool is accessible
# OpenCode exposes: task, explore, librarian, metis, momus, oracle

# Codex CLI detection
# Check if running inside Codex session
echo ${CODEX_SESSION_ID:+found}

# Gemini detection
# Gemini CLI doesn't have native agent dispatch (yet)
# Check for subagent enablement: .gemini/settings.json experimental.enableAgents
```

**Environment Variables** (use as backup signals, not primary detection):

| Variable              | Executor    | Reliability          |
| --------------------- | ----------- | -------------------- |
| `CLAUDE_CODE_SESSION` | Claude Code | Low (may not be set) |
| `CODEX_SESSION_ID`    | Codex CLI   | Medium               |
| `OPENCODE_SESSION_ID` | OpenCode    | Low (may not be set) |
| `OPENCODE_CLIENT`     | OpenCode    | Medium               |

**Primary Detection** should always be tool availability checks, not environment variables.

---

### Step 2: Enumerate Available Tools

Check what dispatch mechanisms are available:

```yaml
native_dispatch:
  # Claude Code
  claude_task_tool:
    check: "Can invoke Task tool with subagent_type parameter"
    agents: ["explore", "librarian", "oracle", "metis", "momus"]

  # OpenCode
  opencode_task_tool:
    check: "Can invoke task tool (lowercase)"
    agents: ["explore", "librarian", "metis", "momus", "oracle", "general"]

  # Codex native dispatch
  codex_multi_agent:
    check: "codex features list shows multi_agent enabled"
    agents: [] # Codex spawns domain experts internally

  # Gemini subagents
  gemini_subagents:
    check: ".gemini/settings.json has experimental.enableAgents: true"
    agents: [] # Gemini spawns subagents internally

mcp_tools:
  codex:
    check: "mcp__codex__codex tool is accessible"
    tools: ["mcp__codex__codex", "mcp__codex__codex-reply"]

  # Other MCP servers...

cli_tools:
  codex:
    check: "which codex returns path"

  gemini:
    check: "which gemini returns path"

  opencode:
    check: "which opencode returns path"
```

---

### Step 3: Return Capability Manifest

The discovery function returns a standardized capability manifest:

```json
{
  "executor_type": "claude-code | opencode | codex | gemini | unknown",
  "executor_version": "detected version if available",
  "session_id": "current session ID if available",

  "native_dispatch": {
    "available": true,
    "tool_name": "Task | task | null",
    "subagent_types": ["explore", "librarian", "oracle", "metis", "momus"],
    "session_continuity": true
  },

  "mcp_tools": {
    "available": true,
    "servers": ["codex", "other-mcp-server"],
    "tools": ["mcp__codex__codex", "mcp__codex__codex-reply"]
  },

  "cli_tools": {
    "codex": { "available": true, "path": "/usr/local/bin/codex" },
    "gemini": { "available": false, "path": null },
    "opencode": { "available": true, "path": "/usr/local/bin/opencode" }
  },

  "recommended_dispatch": "native | mcp | cli | none",

  "limitations": {
    "approval_required": false,
    "sandbox_mode": "read-only | workspace-write | full-access",
    "max_concurrent_agents": 10
  }
}
```

---

## Executor-Specific Detection Details

### Claude Code

**Primary Signal**: Task tool is accessible with `subagent_type` parameter

```javascript
// Detection logic (pseudocode - not actual code to execute)
if (canInvokeTask && Task.supportsParameter("subagent_type")) {
  return {
    executor_type: "claude-code",
    native_dispatch: {
      available: true,
      tool_name: "Task",
      subagent_types: ["explore", "librarian", "oracle", "metis", "momus"],
      session_continuity: true, // Parent agent holds all state
    },
  };
}
```

**Dispatch characteristics**:

- Full Agent Teams support with async messaging
- Session continuity via parent agent
- Can spawn parallel agents with different subagent_types
- Native debate-protocol integration

---

### OpenCode

**Primary Signal**: `task` tool (lowercase) is accessible

```javascript
// Detection logic
if (canInvokeTask && task.supportsSubagentTypes) {
  return {
    executor_type: "opencode",
    native_dispatch: {
      available: true,
      tool_name: "task",
      subagent_types: [
        "explore",
        "librarian",
        "metis",
        "momus",
        "oracle",
        "general",
      ],
      session_continuity: true,
    },
  };
}
```

**Dispatch characteristics**:

- Multiple built-in agent types (explore, librarian, oracle, etc.)
- Session continuity through HTTP API sessions
- Can run parallel agents
- Supports both HTTP API and CLI dispatch

**Key difference from Claude Code**: OpenCode uses lowercase `task` tool, Claude Code uses uppercase `Task`.

---

### Codex CLI

**Primary Signals**:

1. Running inside Codex session (`CODEX_SESSION_ID` set)
2. `codex features list` shows `multi_agent` enabled

```bash
# Native dispatch detection
CODEX_SESSION_ID=${CODEX_SESSION_ID:-}
if [ -n "$CODEX_SESSION_ID" ]; then
  codex features list 2>/dev/null | grep -q "multi_agent.*enabled"
  if [ $? -eq 0 ]; then
    echo "native-dispatch: available (multi-agent mode)"
  else
    echo "native-dispatch: unavailable (single-agent mode)"
  fi
fi
```

**Dispatch characteristics**:

- Multi-agent mode spawns domain experts in parallel
- Single-agent mode: one Codex session reviews all domains
- MCP path available via `mcp__codex__codex`
- CLI fallback via `codex exec`
- Session continuity via `codex-reply` (MCP) or `threadId` (native)

---

### Gemini CLI

**Primary Signals**:

1. `.gemini/settings.json` has `experimental.enableAgents: true`
2. `gemini --version` succeeds

```bash
# Subagent mode detection
if [ -f ".gemini/settings.json" ]; then
  ENABLED=$(cat .gemini/settings.json | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('experimental',{}).get('enableAgents', False))")
  if [ "$ENABLED" = "True" ]; then
    echo "native-dispatch: available (subagent mode)"
  else
    echo "native-dispatch: unavailable"
  fi
fi

# Also check user-level settings
if [ -f ~/.gemini/settings.json ]; then
  # Same check...
fi
```

**Dispatch characteristics**:

- Subagent mode: spawn specialized Gemini subagents
- No subagent mode: single Gemini call covers all domains
- Stateless context passing between rounds
- CLI only (no MCP server)

---

## Dispatch Decision Matrix

After discovery, use this matrix to select the dispatch path:

| Executor        | Native        | MCP            | CLI            | Priority                |
| --------------- | ------------- | -------------- | -------------- | ----------------------- |
| **Claude Code** | ✓ Task tool   | ✓ configured   | N/A            | Native → MCP            |
| **OpenCode**    | ✓ task tool   | ✓ configured   | ✓ opencode run | Native → HTTP API → CLI |
| **Codex**       | ✓ multi-agent | ✓ mcp\_\_codex | ✓ codex exec   | Native → MCP → CLI      |
| **Gemini**      | ✓ subagents   | ✗              | ✓ gemini -p    | Subagent → CLI          |

**Priority rule**: Always prefer native dispatch when available - it provides richer context, session continuity, and parallel execution.

---

## Bridge Integration

Each bridge MUST call the discovery protocol during Step 1 (Pre-Flight):

```yaml
# In bridge-*/SKILL.md

## Step 1: Pre-Flight — Context Discovery

### Step 1.0: Discover Execution Context (NEW - MANDATORY)

Before checking connection availability, discover what dispatch methods
are available in the CURRENT execution context.

Call: discover_context()

Returns: CapabilityManifest (see schema above)

Store: context_caps = result

### Step 1.1: Select Dispatch Path

Based on context_caps.recommended_dispatch:

if context_caps.native_dispatch.available:
  connection_preference = ["native"]
elif context_caps.mcp_tools.available:
  connection_preference = ["mcp"]
elif context_caps.cli_tools.{bridge}.available:
  connection_preference = ["cli"]
else:
  return status: HALTED
```

---

## Implementation Notes

### Stateless Discovery

Discovery checks should be:

- **Fast**: Complete in < 1 second
- **Non-blocking**: Never wait for user input
- **Cacheable**: Results valid for session duration (no TTL needed)
- **Side-effect free**: No file modifications, no network calls (except localhost API checks)

### Discovery vs Availability

Discovery answers: "What CAN I use?"
Availability checks answer: "Is a specific path WORKING?"

Example:

- Discovery: "MCP codex server is configured"
- Availability: "mcp**codex**codex actually responds to a ping"

Run discovery once per bridge invocation. Run availability checks for each candidate path.

### Error Handling

If discovery fails to identify the executor:

1. Default to CLI path (most universal)
2. If CLI also unavailable → return `HALTED` with advisory
3. Never crash or silently skip

---

## Schema Version

- **Version**: 1.0
- **Last updated**: 2026-03-03
- **Breaking changes**: None yet
