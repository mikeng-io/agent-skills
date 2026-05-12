---
name: council-taxonomy
description: Shared vocabulary for Agent Council, Model Council, Runtime Council, and Deep Council. Use before designing or invoking council workflows so role, model, runtime/toolchain, and debate-layer diversity are not conflated.
location: managed
context: reference
---

# Council Taxonomy

This reference defines council primitives used by `agent-council`, `deep-council`, `debate-protocol`, and bridge adapters. Read this before using any council terminology in a skill, lifecycle document, or artifact.

## Core Principle

Deep insight does not come from model diversity alone. Different runtimes using the same model can produce materially different findings because their planning loop, tool affordances, context packaging, file discovery, browser/repo access, session continuity, and error recovery differ.

Council reports must therefore record all diversity sources:

- **Role diversity** — different expert perspectives inside one council.
- **Model diversity** — different model weights/providers.
- **Runtime diversity** — different agent executors such as Claude Code, Codex, OpenCode, Gemini CLI, Kimi CLI, or Hermes subagents.
- **Toolchain diversity** — different available tools, MCP servers, browser/repo access, and shell/file workflows.
- **Evidence-channel diversity** — different ways of grounding claims: tests, logs, source files, web sources, browser observations, human input.
- **Debate-layer diversity** — local/intra-council debate and cross-council debate.

---

## Council Types

### Agent Council

**Diversity source:** role / perspective.

A **single runtime** runs multiple expert roles using its native sub-agent dispatch mechanism. Roles always include domain experts, Devil's Advocate, and Integration Checker; Synthesis Lead is optional. The specific dispatch mechanism differs per runtime — see each bridge's SKILL.md for details (e.g., `Task` tool in Claude Code, `task` tool in OpenCode, `Agent` tool in Kimi).

Use for:

- Phase-end reviews and local adversarial validation within one runtime
- Architecture/design critique
- Implementation audits

**Key constraint:** Agent Council dispatches sub-agents using the **native mechanism of the current runtime** (see that runtime's bridge document for the specific tool). It does NOT invoke external CLI bridges (e.g., shelling out to `claude`, `codex`, `kimi`, `gemini`). External CLI dispatch belongs to Deep Council or Runtime Council.

Limitations:

- Same runtime/model can share blind spots.
- Strong role prompts do not equal independent tool/runtime diversity.

---

### Model Council

**Diversity source:** model/provider.

One runtime/toolchain dispatches the same task to multiple configured models and synthesizes the results.

Use for:

- Style/quality comparison
- Model-role allocation
- Subjective scoring
- Checking model-specific overconfidence

Limitations:

- If all models receive the same over-specified prompt through the same runtime, they may share the same framing and tool-context blind spots.

---

### Runtime Council

**Diversity source:** runtime/toolchain/agent loop.

Multiple agent runtimes review or brainstorm the same scope. The models may be identical or different; the runtime/tool flow is the key independent variable.

Examples:

- Claude Code local council
- Codex local council
- OpenCode local council or model council
- Gemini CLI council
- Kimi CLI council
- Hermes subagent council

Use for:

- Surfacing tool-affordance discoveries
- Comparing repo exploration strategies
- Validating whether findings survive different execution flows
- Identifying runtime-specific blind spots

---

### Deep Council

**Diversity source:** composed role + model + runtime + toolchain + debate layers.

Deep Council is a **council-of-councils**. Each bridge/runtime runs a local council using its native strengths. The root orchestrator then runs cross-council debate over the local reports.

```text
Deep Council
├─ Claude Code bridge
│  └─ local Agent Council
├─ Codex bridge
│  └─ local Agent Council
├─ OpenCode bridge
│  └─ local Agent Council or Model Council
├─ Kimi bridge
│  └─ local Agent Council
└─ Cross-Council Debate
   ├─ frame comparison
   ├─ finding challenge
   ├─ shared-bias challenge
   └─ final synthesis
```

Deep Council is not merely "multi-model review." It is layered adversarial synthesis across independently operating councils.

**Deep Council ≠ Runtime Council:** Runtime Council is one layer (multiple runtimes, same task). Deep Council composes Runtime Council + Agent Council + Model Council + cross-council debate. They overlap but are not the same.

---

## "Local Council" — Contextual Role, Not a Type

**"Local council" is not a named council type.** It is a contextual role that any Agent Council, Model Council, or runtime-specific review plays when it runs _inside a bridge_ as the intra-bridge component of Deep Council (Layer 2).

```
Deep Council (orchestrator)
  ├── bridge-claude executor
  │     └── runs Agent Council  ← this is the "local council" for this bridge
  ├── bridge-kimi executor
  │     └── runs Agent Council  ← this is the "local council" for this bridge
  └── Cross-bridge synthesis    ← Layer 1
```

When a bridge document says `local_council_required: true`, it means: "run the richest Agent Council or Model Council this runtime supports before returning to the orchestrator."

**Never use "local council" as a council type in an artifact.** Use the actual type: `agent-council`, `model-council`, or `runtime-native-review` (degraded fallback — not a full council).

---

## Brainstorm vs Review

Councils can run in different modes:

- **review/audit mode:** produce findings and validate them adversarially.
- **brainstorm/design mode:** produce competing proposals, challenge assumptions, merge or reject proposals, and converge on a design recommendation.
- **research mode:** produce evidence-backed observations, contradictions, and confidence-scored synthesis.

Brainstorm-mode councils must not be forced into finding/severity schemas. They use proposal lifecycle states instead.

---

## Discovery-First Context Discipline

Round 1 of any council intended for discovery or brainstorming must receive a minimal, non-leading packet:

Include:

- artifact or topic scope
- user goal / objective
- hard constraints
- allowed mutation level
- broad domains, if useful
- output contract

Exclude:

- expected findings
- suspected root cause
- coordinator's preferred architecture
- other participants' findings
- desired verdict
- implementation narrative presented as truth

Later rounds may introduce proposal inventories, findings, challenges, prior reports, and reconciliation packets.

---

## Common Confusion Points and Anti-Patterns

### Anti-Pattern 1: "Local Council" without definition

**Wrong:** "Ran a local council on this change."

**Right:** "Ran an Agent Council (role diversity, `delegate_task` sub-agents, within the current runtime) on this change."

Why: "Local council" is ambiguous — it could mean Agent Council inside one runtime, or the intra-bridge component of Deep Council. Always name the type explicitly.

---

### Anti-Pattern 2: Deep Council overhead when Agent Council suffices

**Wrong:** Dispatching Claude Code CLI, Codex CLI, and Gemini CLI for a routine phase-end review that only needs role diversity.

**Right:** Run an Agent Council using `delegate_task` sub-agents within the current runtime. Reserve Deep Council / Runtime Council for high-stakes decisions where runtime/toolchain diversity materially improves confidence.

Why: External CLI dispatch is Deep Council overhead. It introduces latency, requires bridge availability, and adds complexity. Agent Council is sufficient when the goal is role diversity, not runtime diversity.

---

### Anti-Pattern 3: Fabricating council findings when a bridge is unavailable

**Wrong:** Returning fabricated findings labeled as "Claude Code review" when the `claude` CLI is not installed.

**Right:** Return `status: SKIPPED` for that bridge, document the gap in the council artifact, and proceed with whatever bridges are available.

Why: Fabricated findings corrupt multi-model confirmation reliability — the entire value of runtime diversity is that findings are independently produced. A SKIPPED bridge with transparent documentation is always preferable to a fabricated report.

---

### Anti-Pattern 4: Calling runtime diversity "Agent Council"

**Wrong:** "We ran an Agent Council using Claude Code, Codex, and Gemini."

**Right:** "We ran a Runtime Council (or Deep Council) dispatching Claude Code, Codex, and Gemini bridges."

Why: Agent Council = role diversity inside one runtime. Dispatching multiple runtimes = Runtime Council / Deep Council. Conflating them hides the actual diversity source and makes the artifact misleading.

---

## Quick Reference

| Term | Type? | Diversity source | Dispatch mechanism |
|------|-------|-----------------|-------------------|
| Agent Council | Named type | Role / perspective | `delegate_task` within current runtime |
| Model Council | Named type | Model / provider | Same runtime, multiple model targets |
| Runtime Council | Named type | Runtime / toolchain | Multiple agent runtimes |
| Deep Council | Named type | All of the above + cross-debate | Council-of-councils via bridge adapters |
| Local Council | Contextual role | Depends on type | Intra-bridge component of Deep Council |

---

## Required Reporting Fields

Council artifacts should record:

```json
{
  "council_type": "agent-council | model-council | runtime-council | deep-council",
  "mode": "review | audit | brainstorm | design | research | synthesis",
  "diversity_sources": ["role", "model", "runtime", "toolchain", "evidence", "debate-layer"],
  "participants": [],
  "models_used": [],
  "runtimes_used": [],
  "toolchains_used": [],
  "exchange_modes_used": [],
  "debate_layers": [],
  "context_policy": "minimal-non-leading | packetized-summary | full-context | targeted-challenge"
}
```

---

## Project-Specific Governance

Project-specific closure rules should live in the consuming project docs. For example, a project may require every phase to end with an Agent Council artifact and every major milestone to run Deep Council when bridge runtimes are available.
