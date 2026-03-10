# Deep Skills Suite

A collection of composable, model-agnostic, domain-agnostic AI agent skills for multi-agent analysis, verification, research, and multi-model council review.

## Overview

Skills are **conversation-driven** — they extract context from what you've been discussing and act on it. No configuration or keywords needed.

**Architecture principles:**
- **Inline execution** — context-sensitive skills run in the same agent, inheriting full conversation history
- **Isolated execution** — stateless data-retrieval skills (`brave-search`, `perplexity`, `deepwiki`) run as isolated sub-agents
- **Progressive enhancement** — each skill works standalone; multi-agent debate and multi-model council are additive layers
- **Non-blocking bridges** — unavailable CLI tools produce `SKIPPED`, never halt execution

---

## Installing Skills

### Via skillsmp.com

Browse and install skills from the registry at [skillsmp.com](https://skillsmp.com/).

### Via skills.sh

```bash
# Install individual skills
npx skills add mikeng-io/agent-skills --skill deep-review
npx skills add mikeng-io/agent-skills --skill deep-audit
npx skills add mikeng-io/agent-skills --skill deep-verify
npx skills add mikeng-io/agent-skills --skill deep-research
npx skills add mikeng-io/agent-skills --skill deep-explorer
npx skills add mikeng-io/agent-skills --skill deep-council

# Install the full suite at once
npx skills add mikeng-io/agent-skills --all
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/mikeng-io/agent-skills
cd agent-skills

# Required foundation (deep-* skills depend on these)
ln -s $(pwd)/skills/domain-registry ~/.claude/skills/domain-registry
ln -s $(pwd)/skills/context ~/.claude/skills/context
ln -s $(pwd)/skills/preflight ~/.claude/skills/preflight
ln -s $(pwd)/skills/parallel-workflow ~/.claude/skills/parallel-workflow
ln -s $(pwd)/skills/debate-protocol ~/.claude/skills/debate-protocol

# Deep skills
ln -s $(pwd)/skills/deep-explorer ~/.claude/skills/deep-explorer
ln -s $(pwd)/skills/deep-review ~/.claude/skills/deep-review
ln -s $(pwd)/skills/deep-audit ~/.claude/skills/deep-audit
ln -s $(pwd)/skills/deep-verify ~/.claude/skills/deep-verify
ln -s $(pwd)/skills/deep-research ~/.claude/skills/deep-research
ln -s $(pwd)/skills/deep-council ~/.claude/skills/deep-council

# Optional — multi-model council bridges
ln -s $(pwd)/skills/bridge-commons ~/.claude/skills/bridge-commons
ln -s $(pwd)/skills/bridge-claude ~/.claude/skills/bridge-claude
ln -s $(pwd)/skills/bridge-gemini ~/.claude/skills/bridge-gemini
ln -s $(pwd)/skills/bridge-codex ~/.claude/skills/bridge-codex
ln -s $(pwd)/skills/bridge-opencode ~/.claude/skills/bridge-opencode
```

---

## Quick Reference

| Goal | Skill | Verdict |
|------|-------|---------|
| Understand codebase or artifact | `/deep-explorer` | No verdict — exploration report |
| Get improvement suggestions | `/deep-review` | Quality assessment |
| Check compliance / standards | `/deep-audit` | PASS / CONCERNS / FAIL |
| Verify correctness, surface risks | `/deep-verify` | PASS / CONCERNS / FAIL |
| Research a topic | `/deep-research` | Evidence-based report |
| Multi-model council review | `/deep-council` | PASS / CONCERNS / FAIL (multi-model confirmed) |

**Example workflows:**

```bash
# Understand a new codebase
/deep-explorer

# Pre-deployment
/deep-audit      # Standards compliance
/deep-verify     # Risk verification

# Research → Implement → Review
/deep-research   # Background research
# ... implement ...
/deep-review     # Improvement suggestions
/deep-council    # Multi-model confidence boost
```

---

## Skills

### Foundation

#### [`context`](./skills/context/)
Classifies the current conversation artifact (code, financial, marketing, etc.), selects domains from the domain registry, and recommends routing (parallel-workflow, debate-protocol, or deep-council). Invokable standalone to inspect how the suite reads your current conversation.

#### [`preflight`](./skills/preflight/)
Lightweight scope clarifier. Invoked by deep-* skills when conversation context is too sparse to determine what to analyze. Asks 1–3 targeted questions one at a time (one per message, multiple-choice preferred), then returns a structured `scope_clarification` block for the calling skill. Skipped automatically when scope is already clear. Adapted from the [superpowers `brainstorming` skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) — same principle of asking before acting, scoped to analysis intent rather than feature design.

#### [`debate-protocol`](./skills/debate-protocol/)
5-phase structured adversarial debate. Domain experts analyze independently, a Devil's Advocate challenges every CRITICAL/HIGH finding, an Integration Checker surfaces cross-component gaps, findings are confirmed/withdrawn/disputed/merged. Used by deep-council and deep-verify.

#### [`parallel-workflow`](./skills/parallel-workflow/)
DAG-based parallel dispatch. Spawns independent sub-agents, collects results, synthesizes. Used by all deep-* skills as their default execution path.

#### [`domain-registry`](./skills/domain-registry/)
Reference library of domain definitions (technical, business, creative). Skills read this to select the right expert roles for any artifact type. Not invokable — read via the `Read` tool.

---

### Deep Skills

#### [`deep-explorer`](./skills/deep-explorer/)
Explores and maps a codebase or artifact. Git-aware: full exploration on first run, delta tracking on subsequent runs.

**Output:** `.outputs/exploration/`

#### [`deep-review`](./skills/deep-review/)
Multi-agent quality improvement review. Spawns domain-appropriate reviewers in parallel. Returns prioritized suggestions — not pass/fail, only improvement-focused.

**Output:** `.outputs/review/`

#### [`deep-audit`](./skills/deep-audit/)
Standards and compliance audit with formal verdicts. Auditor selection driven by domain-registry — a marketing artifact gets brand/legal auditors, a healthcare app gets HIPAA auditors.

**Verdict:** PASS / CONCERNS / FAIL
**Output:** `.outputs/audit/`

#### [`deep-verify`](./skills/deep-verify/)
Risk-focused verification with Devil's Advocate as a mandatory challenger. DAG execution: domain experts → (DA + Integration Checker in parallel) → Third-Party Reviewer. Optional multi-model second pass via `deep-council`.

**Verdict:** PASS / CONCERNS / FAIL
**Output:** `.outputs/verification/`

#### [`deep-research`](./skills/deep-research/)
Multi-domain research with parallel domain researchers. Automatic tool discovery — uses Brave Search, Perplexity, web reader, browser automation, DeepWiki, and documentation query tools as available. Cross-domain synthesis identifies insights that emerge from intersections.

**Output:** `.outputs/research/`

---

### Multi-Model Council

#### [`deep-council`](./skills/deep-council/)
Dispatches the same task to all available AI runtimes in parallel and synthesizes findings across model families. Two-layer debate architecture:

- **Layer 2 (intra-bridge):** Each bridge extracts maximum value from its own model family
- **Layer 1 (cross-bridge):** Debate Coordinator challenges findings across all bridges — multi-model agreement gets elevated, conflicts get flagged

**Bridges:**
| Bridge | Requires | Layer 2 depth |
|--------|----------|--------------|
| `bridge-claude` | Task tool accessible | Full 5-phase debate |
| `bridge-gemini` | `gemini` CLI installed | Post-Analysis Protocol rounds |
| `bridge-codex` | `codex` CLI or MCP configured | Post-Analysis Protocol rounds |
| `bridge-opencode` | `opencode` CLI or server running | Multi-model mini-council if configured |

**Output:** `.outputs/council/`

---

### Optional Data Sources

These run as **isolated sub-agents** (`context: fork`) — stateless lookups, no conversation context needed.

#### [`deepwiki`](./skills/deepwiki/)
Queries a Devin DeepWiki index for a GitHub repository. Returns AI-grounded answers about codebase architecture, component relationships, and design decisions. Requires Devin API key.

```bash
claude mcp add -s user -t http devin https://mcp.devin.ai/mcp -H "Authorization: Bearer <API_KEY>"
```

#### [`brave-search`](./skills/brave-search/)
Brave Search MCP wrapper. Web, news, and local search with an independent index. Requires Brave Search API key.

```bash
claude mcp add -s user brave-search npx @brave/search-mcp
# BRAVE_API_KEY=your_key
```

#### [`perplexity`](./skills/perplexity/)
Perplexity MCP wrapper. Returns AI-synthesized answers with inline citations — best for consensus questions and cross-validation. Requires Perplexity API key.

```bash
claude mcp add -s user perplexity npx @perplexity-ai/mcp-server
# PERPLEXITY_API_KEY=your_key
```

---

## Repository Structure

```
agent-skills/
├── README.md
├── .bridge-settings.json          # Suite config: bridge toggles, opencode models, ttl
│
└── skills/
    ├── TOPOLOGY.md                # Full architecture map, routing decisions, dependency graph
    │
    ├── domain-registry/           # Reference library of domain definitions
    │   ├── README.md
    │   └── domains/
    │       ├── technical.md
    │       ├── business.md
    │       └── creative.md
    │
    ├── bridge-commons/            # Shared contract for all bridge adapters
    │   └── SKILL.md
    │
    ├── debate-protocol/           # 5-phase adversarial debate framework
    │   ├── SKILL.md
    │   ├── experts/
    │   │   ├── devils-advocate.md
    │   │   ├── integration-checker.md
    │   │   ├── test-architect.md
    │   │   └── third-party.md
    │   └── schemas/
    │
    ├── context/                   # Artifact classifier and smart router
    │   └── SKILL.md
    │
    ├── parallel-workflow/         # DAG-based parallel agent dispatcher
    │   └── SKILL.md
    │
    ├── bridge-claude/             # Claude Code sub-agent bridge
    │   └── SKILL.md
    ├── bridge-gemini/             # Gemini CLI bridge
    │   └── SKILL.md
    ├── bridge-codex/              # Codex CLI/MCP bridge
    │   └── SKILL.md
    ├── bridge-opencode/           # OpenCode multi-model bridge
    │   └── SKILL.md
    │
    ├── deep-council/              # Multi-model council orchestrator
    │   ├── SKILL.md
    │   ├── README.md
    │   └── schemas/
    │
    ├── deep-explorer/             # Git-aware codebase exploration
    │   ├── SKILL.md
    │   └── README.md
    │
    ├── deep-review/               # Quality improvement review
    │   ├── SKILL.md
    │   ├── README.md
    │   └── schemas/
    │
    ├── deep-audit/                # Standards compliance audit
    │   ├── SKILL.md
    │   ├── README.md
    │   └── schemas/
    │
    ├── deep-verify/               # Risk verification with DA
    │   ├── SKILL.md
    │   ├── README.md
    │   ├── schemas/
    │   └── validators/
    │
    ├── deep-research/             # Multi-domain research
    │   ├── SKILL.md
    │   ├── README.md
    │   ├── schemas/
    │   └── validators/
    │
    ├── deepwiki/                  # Devin DeepWiki data source
    │   └── SKILL.md
    ├── brave-search/              # Brave Search MCP data source
    │   └── SKILL.md
    └── perplexity/                # Perplexity MCP data source
        └── SKILL.md
```

---

## Skill Execution Model

```
Skill type          context field    Conversation inherited?
─────────────────   ─────────────    ──────────────────────
Deep skills         (none — inline)  Yes — sees full history
Foundation          (none — inline)  Yes — sees full history
Data sources        context: fork    No — stateless lookup
Bridge adapters     context: reference  N/A — read via Read tool, never invoked
```

---

## Configuration

### `.bridge-settings.json`

Suite-level configuration at the repo root:

```json
{
  "bridges": {
    "claude":   { "enabled": true },
    "gemini":   { "enabled": true },
    "codex":    { "enabled": true, "model": null },
    "opencode": { "enabled": true, "model": null, "models": [] }
  },
  "reasoning_level": "medium",
  "ttl_hours": 24
}
```

**`opencode.models`** — set to 2+ model strings to enable multi-model dispatch within bridge-opencode:
```json
"models": ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4o", "google/gemini-2.0-flash"]
```

---

## Design Principles

1. **Non-blocking** — a missing CLI never halts execution; it produces `SKIPPED`
2. **Conversation-driven** — no triggers, keywords, or configuration required
3. **No hardcoded models** — capability levels (`highest`, `high`, `standard`) only
4. **Progressive enhancement** — each skill works at minimum capability; debate and multi-model council are additive
5. **Domain-agnostic** — domain-registry drives expert selection; the same skills work for code, finance, marketing, design, legal
6. **Composable** — any skill can be used standalone or as part of a larger orchestration

---

## Contributing

1. Fork the repository
2. Create your skill under `skills/your-skill/`
3. Follow the skill structure: `SKILL.md` (required), `README.md` (required), `schemas/` (optional)
4. Use capability levels, not model names
5. No `context: fork` unless the skill is stateless and needs no conversation history
6. Submit a pull request

**Skill checklist:**
- [ ] `SKILL.md` with valid frontmatter (name, description, location, allowed-tools)
- [ ] `README.md` with purpose, features, quick start
- [ ] Model-agnostic (capability levels only)
- [ ] Domain-agnostic (domain-registry or conversation-driven selection)
- [ ] Output to `.outputs/{purpose}/` with YAML frontmatter and JSON companion
- [ ] `context: fork` only if stateless (no conversation context needed)
