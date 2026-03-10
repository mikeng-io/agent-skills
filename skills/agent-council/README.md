# Agent Council

Single-model expert council orchestrator. Dispatches multiple expert roles (Devil's Advocate, Integration Checker, Domain Experts) within the SAME model to catch project-specific issues, assumptions, and integration gaps.

## What it does

1. Extracts review scope and domains from conversation context
2. Selects expert roles based on domains and task type
3. Dispatches expert agents in parallel via Task tool (same model, different perspectives)
4. Runs debate protocol between expert perspectives
5. Produces a consolidated expert council report

## When to use it

| Scenario                                      | Use Agent Council | Use Deep Council |
| --------------------------------------------- | ----------------- | ---------------- |
| Multi-model bridges unavailable               | ✓                 | ✗                |
| Quick review, no time for multi-model latency | ✓                 | ✗                |
| Project-specific issues (not model biases)    | ✓                 | ✗                |
| Need maximum confidence via diverse models    | ✗                 | ✓                |
| Catching provider-specific blind spots        | ✗                 | ✓                |

**Agent Council catches project-specific issues. Deep Council catches provider-specific blind spots. They are COMPLEMENTARY.**

## Expert Roles

| Role                | Purpose                                   | Always Present |
| ------------------- | ----------------------------------------- | -------------- |
| Primary Reviewer    | Domain-specific analysis                  | One per domain |
| Devil's Advocate    | Challenge assumptions, find failure modes | ✓              |
| Integration Checker | Surface cross-component implications      | ✓              |
| Synthesis Lead      | Aggregate findings, resolve disputes      | ✓              |

## Architecture

```
agent-council (orchestrator, single model)
├── Task: primary-reviewer-{domain1}
├── Task: primary-reviewer-{domain2}
├── Task: devils-advocate
├── Task: integration-checker
└── Task: debate-coordinator
    └── Synthesis Lead
```

All experts run within the SAME model but receive DIFFERENT role framings. The diversity comes from perspective, not provider.

## Debate Protocol

After initial expert analysis, a mandatory debate round:

1. **Challenge Phase**: Devil's Advocate challenges primary findings
2. **Synthesis Phase**: Integration Checker surfaces cross-component implications
3. **Resolution Phase**: Synthesis Lead resolves disputes and aggregates

Debate outcomes:

- **CONFIRMED**: Finding holds after challenge
- **DOWNGRADED**: Severity reduced
- **DISPUTED**: Challenge has merit but finding not withdrawn
- **WITHDRAWN**: Challenge reveals finding was invalid

## Confidence Tiers

| Tier                     | Meaning                                 |
| ------------------------ | --------------------------------------- |
| `multi_expert_confirmed` | 2+ experts independently surfaced       |
| `single_expert`          | One expert surfaced, survived challenge |
| `integration`            | Cross-component implications            |
| `disputed`               | Challenge not resolved                  |

## Verdict Logic

| Verdict  | Condition                                                 |
| -------- | --------------------------------------------------------- |
| FAIL     | Any multi-expert-confirmed CRITICAL, or 3+ HIGH confirmed |
| CONCERNS | 1-2 HIGH confirmed, or disputed CRITICAL/HIGH             |
| PASS     | No CRITICAL/HIGH confirmed                                |

## Comparison to Deep Council

| Feature             | Agent Council                    | Deep Council                       |
| ------------------- | -------------------------------- | ---------------------------------- |
| **Model Count**     | 1                                | 2-4                                |
| **Expert Roles**    | Multiple                         | Multiple per model                 |
| **Dispatch Method** | Task agents (same model)         | Bridge adapters (different models) |
| **Catches**         | Project-specific assumptions     | Provider-specific blind spots      |
| **Latency**         | Lower (single model)             | Higher (multi-model)               |
| **Availability**    | Always (if Task tool accessible) | Conditional (bridges required)     |
| **Confidence Tier** | Single-model confirmed           | Multi-model confirmed              |

## Availability

Always available when Task tool is accessible (Claude Code, OpenCode, Codex CLI with Task tool). No external CLI or API dependencies.

## Recommendation

1. **Run agent-council first** for quick project reviews
2. **Run deep-council after** when maximum confidence is required
3. **Use both** for critical reviews: catch both project-specific and provider-specific issues

## Schema

Output validated against `schemas/agent-council-report-schema.json`.

## Outputs

Artifacts saved to `.outputs/council/` with YAML frontmatter and JSON companion.
