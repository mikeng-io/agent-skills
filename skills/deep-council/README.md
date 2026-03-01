# Deep Council

Multi-model review council orchestrator. Dispatches reviews to all available bridges (Claude, Gemini, Codex, OpenCode) and synthesizes findings across model families.

## What it does

1. Extracts review scope and domains from conversation context
2. Reads bridge reference docs (bridge-claude, bridge-gemini, bridge-codex, bridge-opencode)
3. Checks which bridges are available (CLI checks, MCP config checks)
4. Dispatches all available bridges in parallel via Task agents
5. Synthesizes findings across bridges: multi-model-confirmed, single-source, disputed
6. Produces a consolidated council report with cross-model verdict

## Why use it?

When you need **maximum confidence** — findings confirmed by multiple model families carry much higher confidence than single-model findings. Deep Council provides:
- **Multi-model confirmation** — highest confidence tier
- **Transparent attribution** — every finding shows which bridge(s) surfaced it
- **Graceful degradation** — works with any 1+ bridges available

## Architecture

```
deep-council (orchestrator)
├── Read: bridge-claude/SKILL.md  ──→ Task: claude bridge executor
│                                       ├── Task: domain expert (per domain)
│                                       ├── Task: Devil's Advocate
│                                       └── Task: Integration Checker
├── Read: bridge-gemini/SKILL.md  ──→ Task: gemini bridge executor
├── Read: bridge-codex/SKILL.md   ──→ Task: codex bridge executor
└── Read: bridge-opencode/SKILL.md ──→ Task: opencode bridge executor
```

## Bridge Availability

| Bridge | Always Available? | Connection |
|--------|------------------|------------|
| claude | Yes | Task tool (native) |
| gemini | Conditional | `which gemini` |
| codex | Conditional | `.mcp.json` or `which codex` |
| opencode | Conditional | `.mcp.json` or `which opencode` |

## Finding Confidence Tiers

| Tier | Meaning |
|------|---------|
| `multi-model-confirmed` | 2+ bridges independently agree |
| `single-source` | 1 bridge surfaced it |
| `disputed` | Bridges disagree |

## Verdict Logic

| Verdict | Condition |
|---------|-----------|
| FAIL | Any multi-model-confirmed CRITICAL, or any CRITICAL from claude bridge |
| CONCERNS | 1-2 HIGH confirmed, or disputed CRITICAL/HIGH |
| PASS | No confirmed CRITICAL/HIGH |

## Fallback Mode

When invoked as a second pass by deep-verify with `--fallback-mode`:
- Uses only bridge-claude (if Task tool accessible in executor environment)
- Marks report `"fallback": true`
- Merges with calling skill's findings

## Schema

Output validated against `schemas/council-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/council/` with YAML frontmatter and JSON companion.
