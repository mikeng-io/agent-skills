# Domain Registry

A reference library of domain knowledge used by deep-* skills to select appropriate expert agents.

## What is this?

Domain Registry is NOT a runnable skill. It is a structured reference library. Skills like `deep-verify`, `deep-audit`, `deep-review`, `deep-explorer`, `deep-research`, and `deep-council` read files from this directory using the `Read` tool to determine which domain experts to spawn for a given review.

## How skills use it

1. Skill analyzes conversation context for signals (file types, topics, concerns)
2. Skill reads `domains/technical.md`, `domains/business.md`, or `domains/creative.md`
3. Skill matches detected signals against each domain's `trigger_signals`
4. Skill selects all matching domains (minimum 1, no maximum)
5. Skill spawns expert agents corresponding to selected domains

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
