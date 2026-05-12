# Hook Wiring: Claude Code

How to register Guardian hooks in Claude Code's `settings.json`.

---

## File location

Claude Code reads hooks from `.claude/settings.json` in the project root.

```
your-project/
├── .claude/
│   └── settings.json   ← add hooks here
└── .guardian/
    ├── guardian.py
    ├── adapters/
    │   └── claude.py
    └── hooks/
        ├── guard-council.py
        └── guard-output.py
```

---

## Minimal wiring (output authority only)

Start here — lowest friction, highest value. Blocks agents from directly
writing council artifacts to `.outputs/`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write(*.outputs/*)",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .guardian/hooks/guard-output.py"
          }
        ]
      },
      {
        "matcher": "Edit(*.outputs/*)",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .guardian/hooks/guard-output.py"
          }
        ]
      }
    ]
  }
}
```

---

## Full wiring (all guards)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write(*.outputs/*)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-output.py"}]
      },
      {
        "matcher": "Edit(*.outputs/*)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-output.py"}]
      },
      {
        "matcher": "Skill(agent-council)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
      },
      {
        "matcher": "Skill(deep-review)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
      },
      {
        "matcher": "Skill(deep-audit)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
      },
      {
        "matcher": "Skill(deep-verify)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
      },
      {
        "matcher": "Skill(deep-research)",
        "hooks": [{"type": "command", "command": "python3 .guardian/hooks/guard-council.py"}]
      }
    ]
  }
}
```

---

## Hook payload format

Claude Code sends a JSON payload to the hook script via stdin:

```json
{
  "tool_name": "Skill",
  "tool_input": {
    "skill": "deep-review",
    "args": "{\"scope\": \"...\", \"mode\": \"review\", \"task_type\": \"review\"}"
  }
}
```

For Write/Edit:
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": ".outputs/review/20260512-120000-abc123.md",
    "content": "---\nskill: deep-review\n..."
  }
}
```

The `adapters/claude.py` adapter handles parsing this payload and mapping it
to the correct `guardian.py` check.

---

## Exit code semantics

| Exit code | Claude Code interprets as |
|-----------|--------------------------|
| `0` | Allow — tool executes normally |
| `1` | Warn — tool executes; warning shown |
| `2` | Block — tool does NOT execute; stderr shown to agent |

The agent sees the block message and can correct the input before retrying.

---

## Verifying hooks are wired

```bash
# Test output guard manually
echo '{"tool_name":"Write","tool_input":{"file_path":".outputs/test.md","content":""}}' \
  | python3 .guardian/hooks/guard-output.py
# Expected: exit 2, BLOCK message

# Test with authority token
GUARDIAN_OUTPUT_AUTHORITY=1 echo '{"tool_name":"Write","tool_input":{"file_path":".outputs/test.md","content":""}}' \
  | python3 .guardian/hooks/guard-output.py
# Expected: exit 0
```
