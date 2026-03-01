# Bridge: Codex

Reference adapter for Codex CLI/MCP. Part of the Deep Skills Suite v2 bridge layer.

## What is this?

A **reference document** read by any orchestrating skill via the `Read` tool. Instructions are embedded into Task agent prompts for bridge execution.

## Connection Methods (Fallback Chain)

1. **MCP** — if Codex MCP server is configured in `.mcp.json`
2. **CLI** — `codex --approval-policy never -p "..."` if `which codex` succeeds
3. **SKIPPED** — if neither available

## Read-Only Enforcement

`--approval-policy never` is MANDATORY on both connection paths. Codex must operate in analysis-only mode.

## Timeout Estimation

Calculated dynamically from scope × intensity multiplier. Never hardcoded.

## Fallback

Returns `status: SKIPPED` on any unavailability. Never blocks.

## Part of

- Deep Skills Suite v2
- Consumed by: any orchestrating skill (e.g., `deep-council`, `deep-review`, `deep-audit`, or custom skills)
