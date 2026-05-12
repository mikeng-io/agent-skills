---
name: council-taxonomy
description: Authoritative vocabulary for the skills suite — tier model, runtime/adapter terms, diversity dimensions, anti-patterns. Every council-related skill reads this first before doing anything else. Installs alongside agent-council as a hard dependency. Read this whenever you encounter the words "council", "tier", "runtime", or "local agent" in any artifact or skill.
location: managed
context: reference
---

# Council Taxonomy — Skills Suite Glossary

Authoritative vocabulary for council, runtime, and dispatch terms used across this skills suite.

**Every council-related skill reads this first.** Confusion between Tier 1 (in-runtime sub-agents) and Tier 3 (multi-runtime + debate) — historically caused by overloaded names like "council" — is resolved by the tier model defined here.

If you are reading this from another skill that read-tooled into it: continue back to that skill once you have the vocabulary. This file is a reference document — it is not invoked as a standalone skill via the Skill tool.

---

## Core Vocabulary

### Runtime
An AI agent executor: Claude Code, Codex CLI, Gemini CLI, Kimi Code, OpenCode, or a custom executor (e.g., Hermes). Each runtime has its own native tools, sub-agent dispatch mechanism, model defaults, and tool surface.

### Runtime adapter
A skill that defines how to dispatch a council task to a specific runtime. Lives at `skills/runtime-{name}/SKILL.md`. Examples: `runtime-claude`, `runtime-codex`, `runtime-kimi`, `runtime-gemini`, `runtime-opencode`. Each adapter is a reference document — read via the `Read` tool and embedded into an executor agent's prompt. *(Historically called "bridge-\*".)*

### Runtime contracts
The shared schema all runtime adapters implement: input format, output schema, capability profiles, status values, agent prompt template, artifact format, and the post-analysis protocol. Lives at `skills/runtime-contracts/SKILL.md`. *(Historically `bridge-commons`.)*

### Local agent / sub-agent
An agent dispatched inside a single runtime using its native mechanism — for example, `Task` in Claude Code, `task` (lowercase) in OpenCode, `delegate_task` in Hermes, the `Agent` tool in Kimi, multi-agent dispatch in Codex or Gemini when enabled. "Local" always means **inside one runtime** — it does not cross runtime boundaries.

### Agent Council
The unified multi-agent review skill. Takes a `tier` parameter (0/1/2/3) that scales from a single review (Tier 0) through an in-runtime dispatch (Tier 1) up to a cross-runtime council with debate (Tier 3). This single skill replaces the historical separate names "Agent Council," "Runtime Council," and "Deep Council."

### Tier
The scale parameter of Agent Council. Tier 0 = single agent. Tier 1 = in-runtime. Tier 2 = cross-runtime. Tier 3 = cross-runtime + debate. See **The Tier Model** below.

### Domain
A subject area an expert focuses on (e.g., security, performance, accessibility, data integrity). Resolved from `domain-registry/domains/*.md` by matching `trigger_signals` against conversation context.

### Domain expert
A sub-agent (Tier 1) or a runtime-adapter invocation (Tier 2+) playing the role of an expert in one domain.

### Devil's Advocate (DA)
A fixed cross-domain role that challenges every CRITICAL and HIGH finding produced by domain experts. Present at every tier ≥ 1.

### Integration Checker (IC)
A fixed role that surfaces cross-component issues missed by per-domain experts — interface mismatches, undocumented contracts, error-propagation gaps, ordering dependencies. Present at every tier ≥ 1.

### Diversity dimensions
Orthogonal axes a council can vary along: **role**, **model**, **runtime**, **toolchain**, **evidence-channel**, **debate-layer**. Independent of tier. A Tier 1 council with multiple models configured has model diversity without runtime diversity. See **Diversity Dimensions** below.

### Capability profile
`inspect` (no state changes) or `modify` (can edit files). Derived from `task_type` in the council input. Inspect: review, audit, research, analysis, planning. Modify: implementation. Each runtime adapter translates the profile into its own runtime-specific flags or sandbox values.

### Status values
- `COMPLETED` — task ran and outputs are available
- `SKIPPED` — non-fatal unavailability (runtime missing, timeout, parse failure) — continue with what completed
- `HALTED` — requires user decision (no provider configured, explicit abort)
- `ABORTED` — user stopped the entire operation

### Cross-domain signal
A flag emitted by a domain expert in its output, indicating that another domain should also examine a finding. Triggers dynamic addition of new domain experts in the next debate round. Mechanism is defined in `runtime-contracts`.

### Multi-agent enablement
Whether a runtime supports sub-agent dispatch out of the box.

| Runtime | Default | Enablement required |
|---------|---------|---------------------|
| Claude Code | On | None for `Task` tool; Agent Teams needs `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| OpenCode | On | None |
| Kimi Code | On | None (`Agent` tool is built-in) |
| Gemini CLI | Off | `experimental.enableAgents: true` in `.gemini/settings.json` |
| Codex CLI | Off | `codex features list` must show `multi_agent` enabled |

### Tier escalation
The orchestrator may re-dispatch at a higher tier if a lower-tier council surfaces too many disputed findings, indicates low confidence, or runs into runtime-specific blind spots. Tiers are escalatable; do not commit to a tier prematurely if confidence is borderline.

---

## The Tier Model

| Tier | Label | Scope | When to use |
|------|-------|-------|-------------|
| **Tier 0** | Single Review | 1 agent, no diversity | Trivial scope, 1 domain, council overhead unjustified |
| **Tier 1** | Local Agent Council | 1 runtime, N sub-agents (typically 3–5: domain experts + DA + IC) | ≤5 domains, low-medium granularity, single-runtime context — e.g., a Hermes phase review |
| **Tier 2** | Cross-Runtime Council | M runtimes × N sub-agents each — each runtime runs its own internal Tier 1 | 5–10 domains, need toolchain or model-family diversity, independent verification |
| **Tier 3** | Cross-Runtime Council with Debate | Tier 2 + cross-runtime synthesis round with shared-bias challenge | 9–10+ domains, highest stakes (security, compliance, irreversible decisions), maximum confidence required |

### Picking a tier

1. **Default to Tier 1.** Most reviews are low-medium granularity, single-runtime appropriate.
2. **Escalate to Tier 2** when you need diversity beyond role: different toolchains, different model families, independent verification of a finding.
3. **Escalate to Tier 3** when shared-bias detection matters: high stakes, the cost of all runtimes agreeing for the wrong reason is unacceptable.
4. **Drop to Tier 0** only when even Tier 1 is overkill — single-domain trivial review with no integration concerns.

### Dispatch mechanics by tier

| Tier | Dispatches | Reads runtime adapters? | Cross-runtime debate? |
|------|-----------|------------------------|----------------------|
| 0 | 1 single agent | No | No |
| 1 | N native sub-agents (in-runtime) | No | No |
| 2 | M runtime adapters in parallel, each runs its own Tier 1 | Yes | No |
| 3 | Same as Tier 2, plus cross-runtime synthesis round | Yes | Yes |

---

## Diversity Dimensions

A council's diversity is described by which dimensions are active, **orthogonal to tier**:

| Dimension | What varies | Activated by |
|-----------|------------|-------------|
| **Role** | Domain expert perspectives | Always — domain experts + DA + IC |
| **Model** | Underlying LLM weights | Multi-model runtime config (e.g., OpenCode `models` array, multiple model invocations) |
| **Runtime** | Agent executor (Claude Code, Codex, etc.) | Tier 2+ — runtime adapters dispatched in parallel |
| **Toolchain** | Available tools, MCP servers, browser/repo access | Implicit in runtime selection |
| **Evidence-channel** | How claims are grounded — tests, logs, source files, web sources, browser observations | Task design + runtime selection |
| **Debate-layer** | Cross-council synthesis with shared-bias challenge | Tier 3 only |

Every council artifact must record which dimensions are active in its `diversity_sources` field. A Tier 2 council with two multi-model runtimes has role + model + runtime + toolchain diversity. A Tier 1 council has only role diversity (and model diversity if multi-model is configured at the runtime level).

---

## Common Confusion Points and Anti-Patterns

### Anti-Pattern 1: "I ran a council" without naming the tier

**Wrong:** "Ran an Agent Council on this change."

**Right:** "Ran a Tier 1 Local Agent Council (3 sub-agents in Hermes)."

Without the tier, the consumer can't tell whether you spawned 3 sub-agents or dispatched 5 runtime adapters. The artifact's `tier` field is mandatory.

### Anti-Pattern 2: "Local council" without first establishing tier

**Wrong:** "Confirmed by a local council."

**Right:** "Confirmed by a Tier 1 council in the Hermes runtime." After establishing tier, "local council" is acceptable shorthand within the same artifact.

"Local" always means in-runtime (Tier 1). It is never a council *type* — it is a description of dispatch scope.

### Anti-Pattern 3: Tier inflation

**Wrong:** Dispatching Tier 3 (all five runtime adapters + cross-runtime debate) for a 2-domain code-style review.

**Right:** Tier 1 with 3 sub-agents.

Tier inflation wastes time, burns context window, and devalues Tier 3 signals when they actually matter. Match tier to scope.

### Anti-Pattern 4: Tier deflation

**Wrong:** Dispatching Tier 1 for a 9-domain security/compliance audit because "it's faster."

**Right:** Tier 2 or Tier 3 to surface runtime-specific blind spots that a single runtime cannot self-detect.

A single runtime's blind spots become the audit's blind spots. For high-stakes work, single-runtime confidence is misleading confidence.

### Anti-Pattern 5: Fabricated runtime outputs

**Wrong:** Returning fabricated findings labeled as "from Claude Code review" when the `claude` CLI is not installed.

**Right:** Mark the runtime adapter `SKIPPED`, document the gap in the council artifact, proceed with whatever completed.

Fabricated findings corrupt the entire value proposition of multi-runtime confirmation. SKIPPED with transparent documentation always beats fake confidence.

### Anti-Pattern 6: Confusing diversity with tier

**Wrong:** "We achieved runtime diversity by running OpenCode with three different models."

**Right:** "Tier 1 council in OpenCode with model diversity (three model invocations) — no runtime diversity."

Multi-model dispatch inside a single runtime is **model diversity**, not runtime diversity. Tier 2+ requires multiple runtime adapters. Dimensions are orthogonal to tier.

### Anti-Pattern 7: Saying "Deep Council" or "Runtime Council"

These names are deprecated. Use "Tier 3 Agent Council" and "Tier 2 Agent Council" respectively. The old names obscured that all three are the same skill at different scales.

---

## Old → New Vocabulary Mapping

| Old term | New term |
|----------|----------|
| Agent Council (role-only, single runtime) | Agent Council, Tier 1 |
| Runtime Council | Agent Council, Tier 2 |
| Deep Council | Agent Council, Tier 3 |
| Local council / local review | Tier 1 (in-runtime dispatch) |
| Bridge / bridge adapter | Runtime adapter |
| `bridge-commons` skill | `runtime-contracts` skill |
| `bridge-claude` / `bridge-codex` / `bridge-gemini` / `bridge-opencode` / `bridge-kimi` | `runtime-claude` / `runtime-codex` / `runtime-gemini` / `runtime-opencode` / `runtime-kimi` |
| `.bridge-settings.json` | `.runtime-settings.json` |
| Deep Council escalation | Tier escalation (Tier 1 → 2 → 3) |
| `deep-council` skill | Deleted. Invoke `agent-council` with `tier: 3` |
| `deep-explorer` skill | Deprecated. Codebase exploration handled by `context` skill + runtime's native `explore` sub-agent |

---

## Quick Decision Reference

**"I need a review."**
→ Tier 1 Local Agent Council in your current runtime.

**"I need a review with toolchain/model-family diversity."**
→ Tier 2 — dispatch multiple runtime adapters.

**"I need maximum confidence — this decision is irreversible / high-stakes."**
→ Tier 3 — Tier 2 + cross-runtime debate.

**"This task is trivial / single-domain."**
→ Tier 0 — single agent, no council.

**"The Tier 1 council I just ran has too many disputes."**
→ Escalate to Tier 2 or Tier 3, re-dispatch.

**"A runtime adapter returned SKIPPED."**
→ Continue with what completed. Document the gap. Do not fabricate.

---

## Where to Read Next

- `agent-council/SKILL.md` — the unified, tier-parameterized council skill
- `runtime-contracts/SKILL.md` — the shared contract all runtime adapters implement
- `runtime-{claude,codex,gemini,kimi,opencode}/SKILL.md` — runtime adapter specs
- `domain-registry/README.md` — domain definitions and trigger signals
