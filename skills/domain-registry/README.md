# Domain Registry

A reference library of domain knowledge used by deep-* skills to select appropriate expert agents.

## What is this?

Domain Registry is NOT a runnable skill. It is a structured reference library. Skills like `deep-verify`, `deep-audit`, `deep-review`, `deep-explorer`, `deep-research`, and `deep-council` read files from this directory using the `Read` tool to determine which domain experts to spawn for a given review.

## How skills use it

1. Skill analyzes conversation context for signals (file types, topics, concerns)
2. Skill reads `domains/technical.md`, `domains/business.md`, or `domains/creative.md`
3. Skill matches detected signals against each domain's `trigger_signals`
4. Skill selects all matching domains (minimum 1, no maximum)
5. Skill resolves each domain to an expert using the **Lookup Protocol** below
6. Skill spawns expert agents with the resolved role, focus areas, and standards

---

## Lookup Protocol

The registry is a starting library, not an exhaustive catalog. When resolving a domain signal to an expert, apply this three-tier protocol in order.

### Tier 1 — Exact Match

The detected domain matches a registry entry by name or trigger signals, and the entry's `focus_areas` substantially cover the actual concern.

→ Use `expert_role`, `focus_areas`, and `standards` directly from the entry.

### Tier 2 — Adapted Match

A registry entry is related but not precise. The entry covers the broader domain but not the specific sub-domain or intersection needed.

**Criteria:** The candidate entry's `focus_areas` overlap with the actual need, but the expert role title would be misleading. For example: registry has "Database Architect" for a "database security" concern — the role knows the domain but the focus is wrong.

→ Adapt the entry:
1. Use the registry entry as a base — take only the focus areas that are relevant
2. Supplement with focus areas specific to the actual concern (not in the base entry)
3. Add standards appropriate to the specific need
4. Rename the expert role to reflect the actual task (not the base registry title)

The adapted expert is session-scoped. It is not saved to the registry.

### Tier 3 — Virtual Expert Synthesis

No registry entry provides adequate focus coverage for the specific domain. Using the nearest entry would produce an expert who analyzes the wrong things.

→ Synthesize a session-based virtual expert:

```yaml
virtual_expert:
  name: "{Specific Role Title}"                          # e.g., "Database Security Specialist"
  synthesized_from: ["{registry-domain-1}", ...]         # contributing registry entries, may be empty
  focus_areas:
    - "{area specifically relevant to the actual concern}"
    - ...
  standards:
    - "{standard relevant to this specific domain}"
    - ...
  scope: session   # ephemeral — not persisted to registry
```

Construction steps:
1. Identify contributing registry entries (0, 1, or more)
2. Extract only the focus areas relevant to the specific concern from each contributor
3. Add focus areas not present in any registry entry but required for the specific domain
4. Select standards appropriate to the specific concern
5. Name the role for the specific task, not the contributing base roles

**The key test:** Would an expert with this title, these focus areas, and these standards naturally investigate the actual concern? If not — refine until yes.

### Never substitute a mismatched expert

Do not use a registry entry whose focus areas don't substantially cover the actual need just because it is the closest available option. "Close enough" misses the point:

- A Database Architect reviewing database security will find schema problems, not threat vectors
- A Marketing Strategist reviewing GDPR compliance will find messaging issues, not data-processing violations
- A UX Designer reviewing payment flow security will find usability issues, not PCI scope gaps

When focus is wrong, the findings are wrong. Synthesize rather than misfire.

### When to promote virtual experts to the registry

If a synthesized virtual expert appears in 3 or more sessions for the same domain concern → consider adding it as a permanent entry in the appropriate `domains/*.md` file.

---

## Domain Entry Format

Each domain entry in the domain files follows this structure:

```yaml
- name: domain-name
  trigger_signals:
    - keyword or concept that triggers this domain
    - another keyword
  expert_role: "Title of the expert agent to spawn"
  focus_areas:
    - What the expert focuses on
    - Another focus area
  standards:
    - Relevant standard or framework (e.g., OWASP, WCAG, GAAP)
    - Another standard
```

## Adding New Domains

1. Identify which category fits: `technical`, `business`, or `creative`
2. Add a new entry to the appropriate file in `domains/`
3. Follow the domain entry format above
4. Include at least 3 trigger_signals, 3 focus_areas, and 2 standards

## Domain Categories

- **technical.md** — Software engineering, infrastructure, security, testing
- **business.md** — Finance, legal, product, strategy, marketing, operations
- **creative.md** — Design, UX, content, brand

## No Execution Needed

This registry requires no execution. Skills read it directly using the Read tool:

```
Read: skills/domain-registry/domains/technical.md
Read: skills/domain-registry/domains/business.md
Read: skills/domain-registry/domains/creative.md
```
