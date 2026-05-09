# Agent Council

Role-diverse local council orchestrator. Dispatches multiple expert roles (Devil's Advocate, Integration Checker, Domain Experts, Synthesis Lead) within one runtime/model family to catch local assumptions, failure modes, and integration gaps.

## What it does

1. Extracts review scope, mode, and domains from conversation context
2. Selects expert roles based on domains and task type
3. Dispatches expert agents in parallel via the available local agent mechanism
4. Runs debate protocol between expert perspectives
5. Produces a consolidated expert council report

## When to use it

| Scenario | Use Agent Council | Use Deep Council |
| --- | --- | --- |
| Need fast local role-diverse review | ✓ | Optional |
| Need phase-end closure artifact | ✓ | Optional for high-risk phases |
| Need each bridge/runtime to run its own local council | As child council | ✓ |
| Need runtime/toolchain diversity (Codex vs Claude Code vs OpenCode) | ✗ alone | ✓ |
| Need model diversity inside a bridge | ✗ alone | ✓ if bridge supports Model Council |
| Need cross-council debate | ✗ alone | ✓ |

**Agent Council is the local role-diverse primitive. Deep Council may compose multiple Agent Councils, Model Councils, or runtime-native councils and then run cross-council debate.**

## Modes

- `review` / `audit` — produce findings, challenge them, and return a verdict
- `brainstorm` / `design` — produce competing proposals, challenge assumptions, merge/reject/select proposals, and recommend a direction
- `research` — produce evidence-backed observations, contradictions, confidence levels, and gaps

## Expert Roles

| Role | Purpose | Always Present |
| --- | --- | --- |
| Primary Reviewer | Domain-specific analysis | One per domain |
| Devil's Advocate | Challenge assumptions, find failure modes | ✓ |
| Integration Checker | Surface cross-component implications | ✓ |
| Synthesis Lead | Aggregate findings, resolve disputes | ✓ |

## Architecture

```text
agent-council (local orchestrator)
├── primary-reviewer-{domain1}
├── primary-reviewer-{domain2}
├── devils-advocate
├── integration-checker
└── debate-coordinator / synthesis lead
```

Experts run within the same local runtime/model family but receive different role framings. Diversity comes from perspective and adversarial structure, not independent runtime/toolchain paths.

## Debate Protocol

After initial expert analysis, a mandatory debate round:

1. **Challenge Phase** — Devil's Advocate challenges primary findings
2. **Synthesis Phase** — Integration Checker surfaces cross-component implications
3. **Resolution Phase** — Synthesis Lead resolves disputes and aggregates

Debate outcomes:

- **CONFIRMED** — finding holds after challenge
- **DOWNGRADED** — severity reduced
- **DISPUTED** — challenge has merit but finding not withdrawn
- **WITHDRAWN** — challenge reveals finding was invalid

## Brainstorm Mode

Brainstorm mode generates proposals before critique. Round 1 receives minimal, non-leading context only: scope, objective, constraints, and output contract. Later rounds publish proposal inventories, challenge assumptions, revise/merge/split proposals, and converge on an accepted direction.

## Confidence Tiers

| Tier | Meaning |
| --- | --- |
| `multi_expert_confirmed` | 2+ experts independently surfaced |
| `single_expert` | One expert surfaced, survived challenge |
| `integration` | Cross-component implications |
| `disputed` | Challenge not resolved |

## Verdict Logic

| Verdict | Condition |
| --- | --- |
| FAIL | Any multi-expert-confirmed CRITICAL, or 3+ HIGH confirmed |
| CONCERNS | 1-2 HIGH confirmed, or disputed CRITICAL/HIGH |
| PASS | No CRITICAL/HIGH confirmed |

## Comparison to Deep Council

| Feature | Agent Council | Deep Council |
| --- | --- | --- |
| Primary diversity | Roles/perspectives | Roles + models + runtimes + toolchains + debate layers |
| Scope | One local runtime/model family | Multiple bridge/runtime councils |
| Dispatch method | Local agents/roles | Bridge adapters, each running a local council when possible |
| Catches | Local assumptions and integration gaps | Cross-runtime blind spots, shared-bias failures, runtime/toolchain-specific discoveries |
| Latency | Lower | Higher |
| Availability | Available when local agent dispatch exists | Conditional on bridges/runtimes |
| Confidence tier | Local debate-confirmed | Cross-council debate-confirmed |

## Availability

Available when the executor can run local agent roles or equivalent subagents. No external bridge CLI is required.

## Recommendation

1. Run `agent-council` as the default local phase-end council
2. Run `deep-council` when runtime/tool diversity, model diversity, or cross-council debate materially improves confidence
3. Use both for critical milestones: local role-diverse review first, then cross-runtime council-of-councils

## Schema

Output validated against `schemas/agent-council-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/council/` with YAML frontmatter and JSON companion.
