# Debate Protocol

Generic 5-phase structured debate protocol for multi-agent review. Model-agnostic and domain-agnostic.

## Overview

Debate Protocol runs expert reviewers through an adversarial debate to surface high-confidence findings. The structured phases prevent premature consensus and surface edge cases.

## Phases

| Phase | Name | Description | Intensity |
|-------|------|-------------|-----------|
| 1 | Independent Investigation | All reviewers work in parallel, no communication | All |
| 2 | Finding Publication | Coordinator broadcasts all findings | All |
| 3 | Challenge Round | Devil's Advocate drives adversarial challenges | standard, thorough |
| 4 | Synthesis | Merge overlapping findings | standard, thorough |
| 5 | Final Verdict | All reviewers submit final positions | All |

## Expert Roster

| Expert | File | Role |
|--------|------|------|
| Devil's Advocate | `experts/devils-advocate.md` | Adversarial challenger, cross-domain synthesizer |
| Integration Checker | `experts/integration-checker.md` | Cross-component impact analysis |
| Test Architect | `experts/test-architect.md` | Coverage and assertion quality |
| Third-Party Reviewer | `experts/third-party.md` | Fresh eyes, clarity assessment |
| Domain Experts | (from domain-registry) | Spawned per selected domain |

## Finding States

| State | Meaning |
|-------|---------|
| `confirmed` | Defended and/or corroborated by >= threshold of reviewers |
| `withdrawn` | Reviewer withdrew after challenge |
| `disputed` | Challenged but not resolved within rounds |
| `merged` | Two findings consolidated |
| `discovered` | Emerged during challenge rounds (not in Phase 1) |

## Intensity Modes

| Mode | Phases | Max Rounds | Use When |
|------|--------|------------|----------|
| `quick` | 1, 2, 5 | 0 | Fast pass, low stakes |
| `standard` | All | 3 | Default for most reviews |
| `thorough` | All | 5 | High stakes, critical systems |

## Usage

Standalone:
```
Invoke: debate-protocol
```

Called by deep-council (embedded in Task prompt, not via Skill tool):
```
The deep-council orchestrator reads this SKILL.md and embeds its
instructions directly into Task agent prompts.
```

## Schema

Output format validated against `schemas/debate-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/debate/` with YAML frontmatter and JSON companion.
