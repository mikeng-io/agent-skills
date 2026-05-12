# Deep Skills Suite — Topology

This document describes the relationship between all skills, how they depend on each other, and how routing decisions are made based on context, complexity, and user input.

**Read `council-taxonomy/SKILL.md` first** for the vocabulary (runtime, runtime adapter, tier, diversity dimensions, etc.) used throughout this document.

---

## Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Skills Suite                                   │
│                                                                     │
│  Foundation                                                         │
│  ├── council-taxonomy     Authoritative vocabulary (mandatory read) │
│  ├── domain-registry      Knowledge base — expert roles & signals   │
│  ├── runtime-contracts    Shared contract — all runtime adapters    │
│  └── debate-protocol      5-phase structured review debate          │
│                                                                     │
│  Context Intelligence                                               │
│  ├── context              Classify artifact, select domains, route  │
│  └── preflight            Ask 1–3 clarifying questions when fuzzy   │
│                                                                     │
│  Runtime Adapters (reference — not invocable standalone)            │
│  ├── runtime-claude       Task tool → claude -p → Anthropic API     │
│  ├── runtime-gemini       gemini -p → SKIPPED                       │
│  ├── runtime-codex        MCP → codex exec → SKIPPED                │
│  ├── runtime-opencode     HTTP API → opencode run → SKIPPED         │
│  └── runtime-kimi         native subagents → kimi --print → SKIPPED │
│                                                                     │
│  Council (the only council skill — tier-parameterized)              │
│  └── agent-council        Tier 0/1/2/3 unified council orchestrator │
│                                                                     │
│  Thin Entry Points (user-invocable, wrap agent-council)             │
│  ├── deep-review          Constructive review — Tier 1 default     │
│  ├── deep-audit           Compliance audit — Tier 2 default        │
│  ├── deep-verify          Spec verification — Tier 2 default       │
│  ├── deep-research        Multi-domain research — Tier 2 default   │
│  └── deep-explorer        DEPRECATED — use context + runtime exp.  │
│                                                                     │
│  Orchestration Primitive                                            │
│  └── parallel-workflow    DAG dispatch — independent sub-agents     │
│                                                                     │
│  Optional Data Sources (invokable standalone or by other skills)    │
│  ├── deepwiki             Devin DeepWiki — codebase wiki Q&A        │
│  ├── brave-search         Brave Search MCP — web/news/local search  │
│  └── perplexity           Perplexity MCP — AI-synthesized answers   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Graph

```
council-taxonomy ◄──────────────────────── agent-council (mandatory Step 0 read)
                                            deep-* skills (mandatory Step 0 read)

domain-registry ◄────────────────────────── all runtime adapters
                                            agent-council
                                            context

runtime-contracts ◄──────────────────────── runtime-claude
                                            runtime-gemini
                                            runtime-codex
                                            runtime-opencode
                                            runtime-kimi
                                            agent-council (Tier 2+ dispatch)

debate-protocol ◄────────────────────────── agent-council (Tier 3 cross-runtime debate)

context ──────────────────────────────► domain selection
                                             routing decision

agent-council ◄──────────────────────────── deep-review (tier=1)
                                            deep-audit (tier=2)
                                            deep-verify (tier=2)
                                            deep-research (tier=2)
  └── reads (at Tier 2+):
      runtime-contracts
      runtime-claude
      runtime-gemini
      runtime-codex
      runtime-opencode
      runtime-kimi
      debate-protocol (Tier 3 only)

parallel-workflow                          Used internally by agent-council
                                            for parallel sub-agent dispatch
```

---

## Tier-Based Execution

The single `agent-council` skill branches on the `tier` parameter. There is no separate "deep-council" — Tier 3 is what was historically called Deep Council.

```
agent-council
│
├── Tier 0: Single Review
│   └── one agent, no diversity, no debate
│
├── Tier 1: Local Agent Council (in-runtime)
│   ├── domain experts (one per domain)
│   ├── Devil's Advocate
│   ├── Integration Checker
│   └── debate (intensity-dependent rounds)
│
├── Tier 2: Cross-Runtime Council
│   └── parallel dispatch to enabled runtime adapters
│       ├── runtime-claude    ─→ runs its own Tier 1 internally
│       ├── runtime-gemini    ─→ runs its own Tier 1 internally
│       ├── runtime-codex     ─→ runs its own Tier 1 internally
│       ├── runtime-opencode  ─→ runs its own Tier 1 internally
│       │                       (multi-model when configured)
│       └── runtime-kimi      ─→ runs its own Tier 1 internally
│
└── Tier 3: Cross-Runtime Council with Debate
    ├── (Tier 2 dispatch)
    └── Cross-runtime synthesis with shared-bias challenge
        ├── frame comparison
        ├── multi-runtime-confirmed finding validation
        ├── single-runtime finding promotion/demotion
        └── integration findings surfaced from cross-runtime comparison
```

**Tier escalation:** A Tier 1 council with 3+ disputed findings or low confidence may auto-escalate to Tier 2 or 3 and preserve the prior report in `tier_history`.

---

## Routing

Every thin entry point (`deep-review`, `deep-audit`, etc.) and direct `agent-council` invocations follow the same path:

```
1. Read council-taxonomy (mandatory)
2. Resolve scope/context (context + preflight)
3. Select tier (from explicit input or heuristics)
4. Call agent-council with task_type, mode, tier, domains
5. agent-council branches on tier (see Tier-Based Execution)
6. Save artifact under .outputs/{type}/
```

---

## Runtime Availability

`agent-council` at Tier 2+ is non-blocking — runtime adapters that are unavailable are skipped and the council continues with whatever is available.

```
Executor is Claude Code     → runtime-claude available (Task tool accessible)
gemini CLI installed        → runtime-gemini available
Codex MCP configured
  OR codex CLI installed    → runtime-codex available
opencode serve running
  OR opencode CLI installed → runtime-opencode available
  + .runtime-settings.json models array has 2+ entries → multi-model dispatch
kimi-code-mcp configured
  OR kimi CLI installed     → runtime-kimi available

Minimum viable Tier 2/3 council: any single runtime adapter that returns COMPLETED
Zero adapters complete → ABORTED (emitted by agent-council)

Tier 0/1 has no runtime adapter dependency — always works in any executor with
native sub-agent dispatch (Claude Code, OpenCode, Kimi, or Hermes via delegate_task).
```

Runtime adapter availability is not guaranteed — all depend on the executor environment and installed tools. See `council-taxonomy` for the multi-agent enablement table and `runtime-contracts` for the full adapter contract.

---

## Component Context Types

`context: fork` spawns an **isolated sub-agent** — no conversation history from the caller. Use for stateless data retrieval.

Skills with **no `context` field** run **inline** in the invoking agent — full conversation history is accessible. Use for anything that needs to analyze "what was just discussed."

`context: reference` skills are read via the `Read` tool and embedded into Task agent prompts. They are never invoked via the Skill tool.

| Component | context | Inherits conversation? | Invocable standalone? |
|-----------|---------|----------------------|-----------------------|
| `council-taxonomy` | reference | n/a | No |
| `domain-registry` | — (pure reference) | n/a | No |
| `runtime-contracts` | reference | n/a | No |
| `runtime-claude` | reference | n/a | No |
| `runtime-gemini` | reference | n/a | No |
| `runtime-codex` | reference | n/a | No |
| `runtime-opencode` | reference | n/a | No |
| `runtime-kimi` | reference | n/a | No |
| `debate-protocol` | *(inline)* | **Yes** | Yes |
| `context` | *(inline)* | **Yes** | Yes |
| `preflight` | *(inline)* | **Yes** | Yes |
| `parallel-workflow` | *(inline)* | **Yes** | Yes |
| `agent-council` | *(inline)* | **Yes** | Yes |
| `deep-review` | *(inline)* | **Yes** | Yes |
| `deep-audit` | *(inline)* | **Yes** | Yes |
| `deep-verify` | *(inline)* | **Yes** | Yes |
| `deep-research` | *(inline)* | **Yes** | Yes |
| `deep-explorer` | *(deprecated)* | n/a | No (deprecated) |
| `deepwiki` | fork | No — stateless lookup | Yes |
| `brave-search` | fork | No — stateless lookup | Yes |
| `perplexity` | fork | No — stateless lookup | Yes |

---

## Key Design Principles

1. **Tier model unification** — One council skill (`agent-council`), parameterized by tier. No separate `deep-council`.
2. **Council-taxonomy is mandatory** — Every council-related skill reads it as Step 0. Vocabulary confusion is the most common failure mode.
3. **Non-blocking runtime adapters** — A missing CLI never halts a session; it produces `SKIPPED`.
4. **Generic, not review-specific** — All components handle review, planning, implementation, analysis, research, audit, and brainstorm.
5. **No hardcoded models** — Every runtime adapter detects the latest available model at runtime.
6. **Progressive enhancement** — Multi-agent enablement, debate, model diversity, and runtime diversity are additive. Each skill works with the minimum available capability.
7. **Composable** — Any skill can be used standalone or as part of a larger orchestration.
8. **Shared contract** — All runtime adapters implement `runtime-contracts` — one schema to learn, five runtimes.

---

## Historical Naming (Deprecated — see council-taxonomy for full mapping)

| Old | New |
|-----|-----|
| Bridge / bridge adapter | Runtime adapter |
| `bridge-commons` | `runtime-contracts` |
| `bridge-{claude,codex,gemini,opencode,kimi}` | `runtime-{claude,codex,gemini,opencode,kimi}` |
| `.bridge-settings.json` | `.runtime-settings.json` |
| Agent Council (role-only) | `agent-council` at Tier 1 |
| Runtime Council | `agent-council` at Tier 2 |
| Deep Council | `agent-council` at Tier 3 |
| `deep-council` skill | Removed — use `agent-council` with `tier: 3` |
| `deep-explorer` skill | Deprecated — use `context` + runtime adapter's native explore |
