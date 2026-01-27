# Agent Skills Repository

A collection of publishable, generic AI agent skills designed to work across different AI systems and domains.

## Overview

This repository contains reusable skills that are:
- **Model-Agnostic:** Work with Claude, GPT, and other AI systems
- **Domain-Agnostic:** Configurable for any technical domain
- **Conversation-Driven:** Extract context from natural conversation
- **Well-Documented:** Clear documentation and examples

## Available Skills

### [deep-verify](./skills/deep-verify/)

Generic multi-agent verification framework with balanced expert analysis.

- **Purpose:** Verify work through multi-dimensional expert analysis
- **Features:**
  - Three-tier expert system (Invariant + Domain + Dynamic)
  - Conversation-driven domain detection
  - Model-agnostic agent dispatch
  - Balanced verification (Devil's Advocate counters confirmation bias)
  - Works for ANY domain (technical, creative, business, legal, etc.)

**Quick Start:**
```bash
# Install the skill
cp -r skills/deep-verify ~/.claude/skills/

# Use the skill - just discuss your work naturally
User: "I implemented OAuth2. Worried about token security."
/deep-verify
```

**Documentation:** See [skills/deep-verify/README.md](./skills/deep-verify/README.md)

---

## Repository Structure

```
agent-skills/
├── skills/
│   └── deep-verify/          # Multi-agent verification framework
│       ├── SKILL.md          # Executable skill definition
│       ├── README.md         # User documentation
│       ├── config/           # Optional configuration files
│       └── examples/         # Usage examples
└── README.md                 # This file
```

---

## Installing Skills

### Manual Installation

```bash
# Copy the skill to your project's .claude/skills/ directory
cp -r skills/deep-verify ~/.claude/skills/

# Or symlink for development
ln -s $(pwd)/skills/deep-verify ~/.claude/skills/deep-verify
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

### Best Practices

1. **Model-Agnostic:** Use capability levels, not model names
2. **Domain-Agnostic:** Work for any domain through conversation analysis
3. **Conversation-Driven:** Extract context from natural discussion
4. **Well-Documented:** Include examples and clear docs
5. **Bounded Scope:** Skills should do one thing well

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
- [ ] Model-agnostic (capability levels, not model names)
- [ ] Domain-agnostic (works for any domain)
- [ ] Conversation-driven (extracts context naturally)
- [ ] Well-documented with examples

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

Inspired by the multi-agent verification patterns from the Trustless project, adapted for generic use across any AI system and domain.
