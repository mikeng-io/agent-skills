# Deep Skills Repository

A collection of publishable, generic AI agent skills designed to work across different AI systems and domains.

## Overview

This repository contains reusable skills that are:
- **Model-Agnostic:** Work with Claude, GPT, and other AI systems
- **Domain-Agnostic:** Configurable for any technical domain
- **Conversation-Driven:** Extract context from natural conversation
- **Well-Documented:** Clear documentation and examples
- **Forked Execution:** Skills run independently without interfering with main conversation

## Available Skills

### [deep-explorer](./skills/deep-explorer/)

Git-based codebase exploration with delta analysis and parallel execution.

**Purpose:** Understand codebase structure, architecture, patterns, and changes

**Features:**
- Git-based delta tracking (committed + uncommitted + untracked changes)
- Parallel exploration with 5 specialized agents (Structure, Technology, Architecture, Workflow, Dependency)
- Full exploration mode for complete understanding
- Delta exploration mode for incremental analysis
- Baseline metadata storage for tracking changes
- Works with dirty working directories (no forced commits)
- Domain-agnostic codebase analysis

**Output:** `.outputs/exploration/` directory with validated, timestamped reports

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-explorer ~/.claude/skills/

# Explore codebase structure and patterns
User: "I need to understand how this auth system works"
/deep-explorer
```

**Documentation:** [skills/deep-explorer/README.md](./skills/deep-explorer/README.md)

---

### [deep-review](./skills/deep-review/)

Multi-agent quality improvement framework with constructive feedback.

**Purpose:** Get actionable suggestions to improve your work (no pass/fail verdict)

**Features:**
- 4 parallel expert reviewers (Best Practices 35%, Code Quality 30%, Alternatives 20%, Performance 15%)
- Constructive feedback focused on improvement, not criticism
- Prioritized suggestions (HIGH/MEDIUM/LOW)
- Alternative approaches with trade-offs
- Positive aspects included (what's already good)
- Domain-agnostic quality analysis
- **No verdicts** - improvement suggestions only

**Output:** `.outputs/review/` directory with validated, timestamped reports

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-review ~/.claude/skills/

# Get improvement suggestions
User: "I implemented OAuth2 authentication. Can you review it?"
/deep-review
```

**Documentation:** [skills/deep-review/README.md](./skills/deep-review/README.md)

---

### [deep-audit](./skills/deep-audit/)

Multi-agent standards and compliance auditing with pass/fail verdicts.

**Purpose:** Check work against established standards and compliance requirements

**Features:**
- 5 parallel specialist auditors (Security 30%, Accessibility 25%, Code Standards 20%, Regulatory 15%, Performance 10%)
- Formal pass/fail verdicts (PASS, PASS_WITH_WARNINGS, FAIL)
- Standards-based checking (OWASP, WCAG, GDPR, HIPAA, PEP8, ESLint, etc.)
- Violation reports with severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Compliance tracking for regulatory requirements
- Remediation plans with priority
- CRITICAL violations block deployment

**Output:** `.outputs/audit/` directory with validated, timestamped reports

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-audit ~/.claude/skills/

# Audit for compliance
User: "Audit this code for security and accessibility"
/deep-audit
```

**Documentation:** [skills/deep-audit/README.md](./skills/deep-audit/README.md)

---

### [deep-verify](./skills/deep-verify/)

Generic multi-agent verification framework with balanced expert analysis.

**Purpose:** Verify work through multi-dimensional expert analysis with risk assessment

**Features:**
- Three-tier expert system (Invariant + Domain + Dynamic)
- Conversation-driven domain detection
- Model-agnostic agent dispatch
- Balanced verification (Devil's Advocate counters confirmation bias)
- Risk scenario analysis
- Works for ANY domain (technical, creative, business, legal, etc.)
- **Standardized output format with validation gates**

**Output:** `.outputs/verification/` directory with validated, timestamped reports

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-verify ~/.claude/skills/

# Use the skill - just discuss your work naturally
User: "I implemented OAuth2. Worried about token security."
/deep-verify
```

**Documentation:** [skills/deep-verify/README.md](./skills/deep-verify/README.md)

---

### [deep-research](./skills/deep-research/)

Generic multi-domain research framework with domain-aware scheduling.

**Purpose:** Perform comprehensive research on any topic through parallel information gathering

**Features:**
- Automatic MCP tool discovery and adaptation
- Browser automation for dynamic content (Playwright, agent-browser)
- Multi-method research (web search, browser crawling, interactive sites)
- Five-phase research methodology (Intent → Planning → Gathering → Analysis → Reporting)
- Domain-aware effort allocation (Primary 70%, Secondary 30%)
- Parallel execution of domain-focused researchers
- Evidence-based findings with clickable source URLs
- Cross-domain insight generation
- **Standardized output format with source quality validation**

**Output:** `.outputs/research/` directory with validated, timestamped reports

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-research ~/.claude/skills/

# Use the skill - state your research topic naturally
User: "Research event sourcing with Kafka for microservices"
/deep-research
```

**Documentation:** [skills/deep-research/README.md](./skills/deep-research/README.md)

---

## When to Use Which Skill?

Choose the right skill based on your goal:

| Goal | Skill | Output |
|------|-------|--------|
| **Understand codebase** | [deep-explorer](./skills/deep-explorer/) | Architecture insights, patterns, structure |
| **Get improvement ideas** | [deep-review](./skills/deep-review/) | Actionable suggestions, alternatives, trade-offs |
| **Check compliance** | [deep-audit](./skills/deep-audit/) | PASS/FAIL verdict, violation reports, remediation |
| **Assess risks** | [deep-verify](./skills/deep-verify/) | Risk scenarios, expert analysis, verification |
| **Research topics** | [deep-research](./skills/deep-research/) | Evidence-based findings, sources, insights |

**Example workflows:**

```bash
# New codebase workflow
/deep-explorer          # Understand structure first
/deep-review            # Get improvement suggestions
/deep-audit             # Check compliance
/deep-verify            # Verify changes work

# Pre-deployment workflow
/deep-audit             # Must pass compliance
/deep-verify            # Verify no risks
# Deploy if both pass

# Learning workflow
/deep-explorer          # Understand current patterns
/deep-research          # Research best practices
/deep-review            # Compare and get suggestions
```

---

## Repository Structure

```
deep-verify/
├── skills/
│   ├── deep-explorer/        # Git-based codebase exploration
│   │   ├── SKILL.md          # Executable skill definition
│   │   ├── README.md         # User documentation
│   │   └── schemas/          # Output format specifications
│   │
│   ├── deep-review/          # Quality improvement framework
│   │   ├── SKILL.md          # Executable skill definition
│   │   ├── README.md         # User documentation
│   │   └── schemas/          # Output format specifications
│   │
│   ├── deep-audit/           # Standards compliance auditing
│   │   ├── SKILL.md          # Executable skill definition
│   │   ├── README.md         # User documentation
│   │   └── schemas/          # Output format specifications
│   │
│   ├── deep-verify/          # Multi-agent verification framework
│   │   ├── SKILL.md          # Executable skill definition
│   │   ├── README.md         # User documentation
│   │   ├── schemas/          # Output format specifications
│   │   ├── validators/       # Validation logic
│   │   ├── config/           # Optional configuration
│   │   │   ├── README.md     # Configuration guide
│   │   │   └── examples/     # Configuration examples
│   │   └── examples/         # Usage examples
│   │
│   └── deep-research/        # Multi-domain research framework
│       ├── SKILL.md          # Executable skill definition
│       ├── README.md         # User documentation
│       ├── schemas/          # Output format specifications
│       ├── validators/       # Validation logic
│       ├── config/           # Optional configuration
│       │   ├── README.md     # Configuration guide
│       │   └── examples/     # Configuration examples
│       └── examples/         # Usage examples
│
└── README.md                 # This file
```

---

## Installing Skills

### Manual Installation

```bash
# Copy individual skills to your project's .claude/skills/ directory
cp -r skills/deep-explorer ~/.claude/skills/
cp -r skills/deep-review ~/.claude/skills/
cp -r skills/deep-audit ~/.claude/skills/
cp -r skills/deep-verify ~/.claude/skills/
cp -r skills/deep-research ~/.claude/skills/

# Or symlink for development
ln -s $(pwd)/skills/deep-explorer ~/.claude/skills/deep-explorer
ln -s $(pwd)/skills/deep-review ~/.claude/skills/deep-review
ln -s $(pwd)/skills/deep-audit ~/.claude/skills/deep-audit
ln -s $(pwd)/skills/deep-verify ~/.claude/skills/deep-verify
ln -s $(pwd)/skills/deep-research ~/.claude/skills/deep-research
```

### Using Multiple Skills Together

All skills work together in complementary ways:

```bash
# Install all skills
cp -r skills/deep-* ~/.claude/skills/

# Complete workflow example
User: "I joined a new project with an unfamiliar codebase"
/deep-explorer          # Understand the architecture

User: "Now I need to add OAuth2 authentication"
/deep-research          # Research best practices
# ... implement feature ...
/deep-review            # Get improvement suggestions
/deep-audit             # Check security compliance
/deep-verify            # Verify it works correctly

# Pre-deployment workflow
User: "Ready to deploy"
/deep-audit             # Must pass compliance checks
/deep-verify            # Must pass risk verification
# Deploy only if both pass
```

---

## Developing Skills

### Skill Structure

Each skill follows this structure:

```
skill-name/
├── SKILL.md          # Required: Executable skill definition
├── README.md         # Required: User documentation
├── config/           # Optional: Configuration files
│   ├── README.md     # Configuration guide
│   └── examples/     # Configuration examples
└── examples/         # Optional: Usage examples
```

### SKILL.md Format

The `SKILL.md` file is the main skill definition that the AI system executes:

```yaml
---
name: skill-name
description: Brief description
location: managed
context: fork
allowed-tools:
  - Read
  - Write
  - Task
---

# Skill Name

When invoked, the AI will:
1. Execute the steps defined here
2. Use the allowed tools
3. Follow the specified logic
```

**Key Attributes:**
- `location: managed` - Skill is managed by the AI system
- `context: fork` - Skill runs independently without affecting main conversation
- `allowed-tools` - Tools the skill can use

### Best Practices

1. **Model-Agnostic:** Use capability levels ("highest", "high", "standard"), not model names
2. **Domain-Agnostic:** Work for any domain through conversation analysis
3. **Conversation-Driven:** Extract context from natural discussion
4. **Well-Documented:** Include examples and clear docs
5. **Bounded Scope:** Skills should do one thing well
6. **Output Structure:** Use `.outputs/{skill-purpose}/` for consistent output paths

### Output Pattern Convention

All skills should follow the output pattern:

```
.outputs/{skill-purpose}/
├── YYYYMMDD-HHMMSS-{skill-purpose}-{topic-slug}.md
├── YYYYMMDD-HHMMSS-{skill-purpose}-{topic-slug}.json
└── latest-{purpose}.md → (symlink to most recent)
```

Examples:
- `deep-verify` → `.outputs/verification/`
- `deep-research` → `.outputs/research/`

---

## Output Format Standardization

Both skills enforce **strict output format validation** to eliminate chaos and ensure consistency:

### Problem: Format Chaos

Without standardization:
- ❌ Verdict could be "PASS", "Pass", "PASSED", "OK", "GOOD"
- ❌ Impact could be "High", "HIGH", "high", "Major", "Severe"
- ❌ Sections could be missing or renamed
- ❌ Reports varied wildly between runs
- ❌ Impossible to automate parsing or processing

### Solution: JSON Schemas + Validation Gates

Both skills now include:

1. **Formal JSON Schemas** (`schemas/`)
   - Define exact structure and field requirements
   - Enforce standardized enum values
   - Validate types and required fields

2. **Validation Gates** (`validators/`)
   - Run automatically before report finalization
   - Validate JSON against schema
   - Check markdown structure
   - Verify cross-consistency
   - Block completion on critical errors

### Results

After standardization:
- ✅ Verdict is exactly "PASS", "PASS_WITH_CONCERNS", or "FAIL"
- ✅ Impact is exactly "LOW", "MEDIUM", "HIGH", or "CRITICAL"
- ✅ All sections consistently present
- ✅ Reports have identical structure every time
- ✅ Easy to parse programmatically
- ✅ Source quality thresholds enforced (research)

**Example validation output:**
```
❌ Validation FAILED

JSON Errors:
- Missing required field: risk_assessment.scenarios
- Invalid verdict value: 'MAYBE' (must be PASS, PASS_WITH_CONCERNS, or FAIL)

Markdown Errors:
- Missing required section: ## Integration Impact

Suggestions:
1. Add risk_assessment.scenarios array with at least one scenario
2. Change verdict to one of the valid values
3. Add ## Integration Impact section
```

---

## Design Philosophy

### Model-Agnostic

Skills use **capability levels** rather than hardcoded model names:

| Capability | Use Case |
|------------|----------|
| `highest` | Complex reasoning, adversarial tasks |
| `high` | Analysis, domain expertise |
| `standard` | Documentation, summaries |

This ensures skills work with any AI system (Claude, GPT, etc.).

### Domain-Agnostic

Skills dynamically detect domains from conversation context, not from predefined keywords or categories:

```
User: "I implemented OAuth2 in auth.go"

→ Detects: Security domain (from "OAuth2", "auth")
→ Spawns: Security Expert agent
→ Returns: Security-focused verification
```

### Conversation-Driven

Skills extract all necessary context from what you discuss naturally:

**No need to:**
- ❌ Configure triggers
- ❌ Specify domains
- ❌ Set up keywords
- ❌ Define file patterns

**Just:**
- ✅ Discuss your work naturally
- ✅ Invoke the skill
- ✅ Get relevant analysis

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a new skill in `skills/your-skill/`
3. Follow the skill structure above
4. Add documentation and examples
5. Submit a pull request

### Skill Submission Checklist

- [ ] Skill follows the standard structure
- [ ] `SKILL.md` is executable (not just documentation)
- [ ] `README.md` with usage examples
- [ ] `config/README.md` with configuration guide (optional)
- [ ] `examples/` with real usage examples
- [ ] Model-agnostic (capability levels, not model names)
- [ ] Domain-agnostic (works for any domain)
- [ ] Conversation-driven (extracts context naturally)
- [ ] Output follows `.outputs/{purpose}/` pattern
- [ ] Well-documented with examples

---

## Key Documentation

### Comprehensive Guides

- **[DEEP_SKILLS_SUITE.md](./DEEP_SKILLS_SUITE.md)** - Complete guide to all five skills and their relationships
- **[STANDARDIZATION.md](./STANDARDIZATION.md)** - Output format standardization implementation
- **[BROWSER_AUTOMATION.md](./BROWSER_AUTOMATION.md)** - Browser automation and tool discovery capabilities

### Individual Skills

- **[skills/deep-explorer/](./skills/deep-explorer/)** - Git-based codebase exploration
- **[skills/deep-review/](./skills/deep-review/)** - Quality improvement framework
- **[skills/deep-audit/](./skills/deep-audit/)** - Standards compliance auditing
- **[skills/deep-verify/](./skills/deep-verify/)** - Multi-agent verification framework
- **[skills/deep-research/](./skills/deep-research/)** - Multi-domain research framework

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

Inspired by multi-agent verification and research patterns, adapted for generic use across any AI system and domain. These skills are designed to be:
- **Portable** - Work across different AI platforms
- **Reusable** - Generic patterns applicable to any domain
- **Extensible** - Easy to customize and extend
- **Transparent** - Clear documentation and examples
