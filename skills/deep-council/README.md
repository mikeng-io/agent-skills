# Deep Council

Council-of-councils orchestrator. Dispatches discovery-first packets to available bridges (Claude, Gemini, Codex, OpenCode), requires each bridge to run the richest local council it supports or report degraded mode, then synthesizes proposals/findings through cross-council debate.

## What it does

1. Extracts review scope, mode, domains, and constraints from conversation context
2. Reads bridge reference docs (bridge-claude, bridge-gemini, bridge-codex, bridge-opencode)
3. Checks which bridges/runtimes are available (Task tool, CLI checks, MCP config checks)
4. Dispatches minimal, non-leading packets to all available bridges in parallel
5. Requires each bridge to return a local council report, degraded-mode report, SKIPPED, or HALTED
6. Synthesizes outputs as multi-source-confirmed, single-source, disputed, withdrawn, and integration findings
7. Produces a consolidated council-of-councils report with cross-council verdict

## Why use it?

Use Deep Council when you need confidence from independent discovery paths — not just more models. Deep Council provides:

- **Runtime/toolchain diversity** — Claude Code, Codex, OpenCode, Gemini, and other bridges explore with different loops and tools
- **Local councils per bridge** — each runtime can run Agent Council, Model Council, or debate-compatible review before reporting
- **Multi-source confirmation** — agreement is tracked across models, runtimes, toolchains, and evidence channels
- **Brainstorm/design mode** — bridges generate competing proposals before cross-council challenge and synthesis
- **Transparent attribution** — every finding/proposal records which bridge(s), runtime(s), and evidence channels produced it
- **Graceful degradation** — works with any 1+ completed bridge; unavailable bridges are recorded, not hidden

## Architecture

```text
deep-council root orchestrator
├── bridge-claude local council
│   ├── domain expert(s)
│   ├── Devil's Advocate
│   └── Integration Checker
├── bridge-gemini debate-compatible council
├── bridge-codex local council / Post-Analysis rounds
├── bridge-opencode local council or Model Council
└── cross-council debate
    ├── frame comparison
    ├── finding/proposal challenge
    ├── shared-bias challenge
    └── final synthesis
```

## Bridge Availability

| Bridge | Always Available? | Connection | Local council expectation |
|--------|------------------|------------|---------------------------|
| claude | Yes when Task tool exists | Task tool | Full local Agent Council / debate-protocol when available |
| gemini | Conditional | `which gemini` | Stateless debate-compatible council / degraded mode if limited |
| codex | Conditional | `.mcp.json` or `which codex` | Local council or Post-Analysis rounds |
| opencode | Conditional | `.mcp.json`, server, or `which opencode` | Local council; Model Council if multiple models configured |

## Context Discipline

Round 1 discovery/brainstorm packets must be minimal and non-leading. Include scope, objective, constraints, and output contract. Do not include expected findings, suspected root causes, preferred architecture, desired verdict, or other bridge outputs until challenge/reconciliation rounds.

## Confidence Tiers

| Tier | Meaning |
|------|---------|
| `multi_source_confirmed` | 2+ independent bridge/runtime/model/evidence sources converge |
| `model-confirmed` | 2+ models converge inside one bridge or across bridges |
| `runtime-confirmed` | 2+ runtimes/toolchains converge |
| `evidence-confirmed` | Claim is backed by source/test/log/document evidence |
| `single-source` | 1 bridge surfaced it and it survived challenge |
| `disputed` | Bridges or debate roles disagree |

## Verdict Logic

| Verdict | Condition |
|---------|-----------|
| FAIL | Any multi-source-confirmed CRITICAL, any strongly evidenced CRITICAL from a high-depth bridge, or 3+ multi-source-confirmed HIGH findings |
| CONCERNS | 1-2 HIGH multi-source-confirmed findings, multiple single-source HIGH findings, or disputed CRITICAL/HIGH |
| PASS | No confirmed CRITICAL/HIGH findings |

## Brainstorm / Design Mode

Brainstorm mode asks each local council to generate independent proposals before any cross-council debate. Later rounds publish proposal inventories, challenge assumptions, merge compatible proposals, reject weak ones, and produce an accepted direction plus open questions.

## Fallback Mode

When invoked as a second pass by deep-verify with `--fallback-mode`:

- Uses available bridge(s), commonly bridge-claude when Task tool is accessible
- Marks report `"fallback": true`
- Merges with calling skill's findings using `multi_source_confirmed`, `single_source_findings`, and `disputed_findings`

## Schema

Output validated against `schemas/council-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/council/` with YAML frontmatter and JSON companion.
