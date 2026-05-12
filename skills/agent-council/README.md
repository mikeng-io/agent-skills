# Agent Council

Unified multi-agent council skill. The single entry point for any council-style review, audit, research, or brainstorm — from a 1-agent trivial review (Tier 0) up to a cross-runtime council with shared-bias debate (Tier 3).

## Tier model

`tier` is the scale parameter. The `agent-council` skill branches on it:

| Tier | Label | Scope |
|------|-------|-------|
| 0 | Single Review | 1 agent, no diversity |
| 1 | Local Agent Council | 1 runtime, N sub-agents (domain experts + DA + IC) |
| 2 | Cross-Runtime Council | M runtimes × N sub-agents each — each runtime runs its own Tier 1 internally |
| 3 | Cross-Runtime Council with Debate | Tier 2 + cross-runtime synthesis with shared-bias challenge |

See `council-taxonomy/SKILL.md` for the full glossary, anti-patterns, and decision matrix. **Read it before using `agent-council`.**

## Replaces

This skill supersedes the historical separate skills `agent-council` (role-only, single runtime) and `deep-council` (multi-runtime + debate). Both are tiers of the same operation:

- Old "Agent Council" → Tier 1
- Old "Runtime Council" → Tier 2
- Old "Deep Council" → Tier 3

## Modes

Mode is independent of tier. Any tier can run any mode:

- `review` / `audit` — produce findings with severity, return verdict
- `brainstorm` / `design` — produce competing proposals, no verdict
- `research` — produce evidence-backed observations and contradictions, no verdict

## When to invoke directly vs. through a wrapper

| Use case | Invoke |
|----------|--------|
| Generic council work, you know the tier | `agent-council` |
| Constructive improvement feedback | `deep-review` (sets tier=1, framing=improvement) |
| Compliance / standards audit | `deep-audit` (sets tier=2, mode=audit, capability-calibrated verdict) |
| Spec verification | `deep-verify` (sets tier=2, attaches spec) |
| Multi-domain research | `deep-research` (sets tier=2, mode=research, observation schema) |

## Architecture

```
agent-council
├── Step 0: Read council-taxonomy (vocabulary)
├── Step 1: Dependency check
├── Step 2: Scope & context (context + preflight)
├── Step 3: Tier selection (explicit or auto)
├── Step 4: Populate council context
├── Step 5: Domain selection (from domain-registry)
├── Step 6: Tier dispatch
│   ├── Tier 0: single agent
│   ├── Tier 1: in-runtime sub-agents via native dispatch
│   ├── Tier 2: parallel runtime adapters → each runs Tier 1 internally
│   └── Tier 3: Tier 2 + cross-runtime synthesis with shared-bias challenge
├── Step 7: Synthesis & verdict
└── Step 8: Save artifact
```

## Dependencies

- `council-taxonomy` — vocabulary (mandatory)
- `context` — artifact classification, domain detection
- `preflight` — clarifying questions when scope is fuzzy
- `domain-registry` — domain definitions
- `runtime-contracts` — shared contract for runtime adapters (formerly `bridge-commons`)
- `runtime-{claude,codex,gemini,opencode,kimi}` — runtime adapters (only loaded at Tier 2+)

## Outputs

Artifacts saved to `.outputs/council/{YYYYMMDD-HHMMSS}-tier{N}-{session_id}.md` with YAML frontmatter and JSON companion. `tier` field is always populated. `diversity_sources` field records which axes were active (role/model/runtime/toolchain/debate-layer).
