# Deep Context

Artifact classifier and smart router for the Deep Skills Suite. Analyzes conversation context to detect domains and determine optimal review routing.

## What it does

1. Analyzes conversation for signals (file types, topics, concerns, explicit mentions)
2. Classifies artifact type (code, financial, marketing, creative, research, mixed)
3. Selects matching domains from domain-registry
4. Recommends routing: `parallel-workflow`, `debate-protocol`, or `deep-council`
5. Produces a context report for use by the calling skill or user

## Usage

Standalone:
```
Invoke: context
```

As pre-flight step (called by other skills inline):
```
Other skill reads context/SKILL.md and applies context analysis
steps before spawning domain experts.
```

## Routing Logic

| Condition | Routing |
|-----------|---------|
| < 3 domains, no high-stakes signals | parallel-workflow |
| >= 3 domains OR high-stakes signals | debate-protocol (standard) |
| "thorough" / "critical" in request | debate-protocol (thorough) |
| Explicit multi-model request | deep-council |

## Confidence Levels

| Level | Meaning |
|-------|---------|
| high | Explicit domain mentions, clear file types |
| medium | Inferred from technical terms, mixed signals |
| low | Minimal context, ambiguous signals |

## Schema

Output validated against `schemas/context-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/context/` with YAML frontmatter and JSON companion.
