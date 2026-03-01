# Bridge: OpenCode

Reference adapter for OpenCode — multi-model bridge. Part of the Deep Skills Suite v2 bridge layer.

## What is this?

A **reference document** read by any orchestrating skill via the `Read` tool. Instructions are embedded into Task agent prompts for bridge execution.

## Why OpenCode is special

OpenCode dispatches to multiple model families internally (GLM, Qwen, MiniMax, etc.). A single OpenCode call provides the highest coverage of any single bridge.

**Trade-off:** 1.5× timeout multiplier due to multi-model internal dispatch.

## Connection Methods (Fallback Chain)

1. **MCP/API** — if OpenCode MCP server is configured in `.mcp.json`
2. **CLI** — `opencode run --prompt "..." --no-interactive` if `which opencode` succeeds
3. **SKIPPED** — if neither available

## Timeout Calculation

`final_timeout = base_scope_timeout × 1.5 (opencode_multiplier) × intensity_multiplier`

Always higher than other bridges due to multi-model overhead.

## Model Attribution

When OpenCode returns model-attributed findings (which model surfaced which finding), the bridge preserves that attribution in the output JSON. This enables richer cross-model analysis by any calling skill.

## Fallback

Returns `status: SKIPPED` on any unavailability. Never blocks.

## Part of

- Deep Skills Suite v2
- Consumed by: any orchestrating skill (e.g., `deep-council`, `deep-review`, `deep-audit`, or custom skills)
