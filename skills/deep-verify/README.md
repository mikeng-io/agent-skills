# Deep Verify

Generic multi-agent verification framework with balanced expert analysis.

## Overview

Deep Verify is a model-agnostic, **domain-agnostic** verification framework that uses multiple AI agents to analyze work from **any domain** through conversation-driven expert selection.

It works for:
- **Technical:** Code, infrastructure, databases
- **Creative:** Design, copywriting, marketing
- **Business:** Strategy, finance, operations
- **People:** HR, management, organizational design
- **Legal:** Contracts, compliance, regulations
- **Any domain** - fully dynamic and elastic

## Key Features

- **Conversation-Driven:** Extracts all context from what you discussed
- **Model-Agnostic:** Works with any available AI model (no hardcoded names)
- **Domain-Agnostic:** Dynamically adapts to ANY domain
- **Intelligent Expert Selection:** Auto-generates experts based on conversation
- **Balanced Verification:** Devil's Advocate counters confirmation bias
- **No Configuration Required:** Works out of the box

## Quick Start

```bash
# Install the skill
cp -r skills/deep-verify .claude/skills/

# Use the skill - just discuss your work naturally
User: "I just implemented OAuth2 authentication. Worried about token security."
/deep-verify

# The skill automatically analyzes the conversation and generates
# a security-focused verification report
```

## How It Works

### 1. You Discuss Your Work

```
User: "I implemented OAuth2 in src/api/auth.go.
      I'm worried about token security and session handling."
```

### 2. Deep Verify Analyzes

Extracts from conversation:
- **Files:** `src/api/auth.go`
- **Topics:** OAuth2, authentication, session
- **Concerns:** token security, session handling
- **Domain:** Security (inferred)

### 3. Experts Are Auto-Selected

```
✓ Devil's Advocate (always)
✓ Integration Checker (always)
✓ Third-Party Reviewer (always)
✓ Security Expert (high confidence from conversation)
```

### 4. Report Generated

Balanced verification report with:
- Risk assessment (Devil's Advocate)
- Domain findings (Security)
- Integration impact
- Recommendations

## Conversation Examples

### Example 1: Code Verification

```
User: "I implemented OAuth2 in src/api/auth.go.
      Worried about token security."

/deep-verify

→ Detects: Security domain (from "OAuth2", "token security")
→ Returns: Security-focused verification
```

### Example 2: Marketing Review

```
User: "I wrote the Q2 product launch email.
      Concerned about tone being too salesy and GDPR compliance."

/deep-verify

→ Detects: Marketing domain (from "email campaign", "tone")
→ Detects: Compliance domain (from "GDPR")
→ Returns: Marketing + compliance verification
```

### Example 3: Design Review

```
User: "Created new dashboard in Figma.
      Worried about accessibility for color blindness."

/deep-verify

→ Detects: Design domain (from "Figma", "dashboard")
→ Detects: Accessibility domain (from "color blindness")
→ Returns: Design + accessibility verification
```

### Example 4: HR Policy

```
User: "Updated remote work policy.
      Concerned about legal compliance across different countries."

/deep-verify

→ Detects: HR domain (from "policy")
→ Detects: Legal domain (from "compliance")
→ Returns: HR + legal verification
```

## Model Selection

Deep Verify is **model-agnostic** - it doesn't hardcode model names:

| Expert Type | Preference | Fallback |
|-------------|------------|----------|
| **Adversarial** | Highest capability available | Any model |
| **Analytical** | High capability | Standard capability |
| **Lightweight** | Standard capability | Any model |

The system auto-detects what's available and uses the best option.

## Expert Selection

### Invariant Experts (Always Run)

- **Devil's Advocate (40%):** Pre-mortem analysis, surfaces hidden risks
- **Integration Checker (15%):** System-wide impact assessment
- **Third-Party Reviewer (5%):** Fresh-eyes perspective

### Domain Experts (Auto-Generated)

Dynamically generated from conversation context through natural language analysis. Any domain can be detected - the system is not limited to predefined categories.

### Dynamic Experts (Auto-Generated)

For specialized or niche topics:
- "Kafka event sourcing" → Kafka Expert, Event Sourcing Expert
- "GDPR Article 17" → GDPR Expert, Legal Expert
- "Color blindness accessibility" → Accessibility Expert, Design Expert

## Output

Reports are saved to a generic output directory:

```
.outputs/verification/
├── YYYYMMDD-HHMMSS-verification-report.md
├── YYYYMMDD-HHMMSS-verification-report.json
└── latest-report.md → (symlink to most recent)
```

**Configurable** via environment variable:

```bash
export DEEP_VERIFY_OUTPUT_DIR=".outputs/reviews/"
```


## Configuration (Optional)

Most projects don't need configuration. But you can optionally configure:

### Expert Weights

```yaml
# .outputs/verification/weights.yaml

weights:
  devils_advocate: 0.40
  integration: 0.15
  third_party: 0.05
  domain_experts: 0.40
```

## Why Conversation-Driven?

Traditional verification frameworks require:
- ❌ Configuring triggers
- ❌ Specifying domains
- ❌ Setting up keywords
- ❌ Defining file patterns

Deep Verify just needs:
- ✅ Discuss your work naturally
- ✅ Invoke /deep-verify
- ✅ Get relevant expert analysis

The system extracts everything from your conversation and dynamically generates appropriate experts.

## Philosophy: Balanced Verification

### The Problem: Confirmation Bias

When you've created something, you're biased toward seeing it as correct:
- Domain experts confirm: "Looks good" ✅
- But nobody asks: **"What could go wrong?"**

### The Solution: Devil's Advocate

Devil's Advocate gets 40% weight (equal to ALL domain experts combined):

```
Without Devil's Advocate:
├── Domain Expert 1: "Looks correct" → +1 confidence
├── Domain Expert 2: "Seems fine" → +1 confidence
└── Result: 100% confidence (confirmation bias)

With Devil's Advocate (40%):
├── Devil's Advocate: "What if X fails?" → -1 confidence
├── Domain Expert 1: "Looks correct" → +0.4 confidence
├── Domain Expert 2: "Seems fine" → +0.4 confidence
└── Result: Balanced view with risks surfaced
```

## Extensibility

The system is fully dynamic:

- **Any domain:** Works for technical, creative, business, people, legal, etc.
- **Any model:** Works with Claude, GPT, or any AI system
- **Elastic:** Automatically adapts to what you discuss

## Documentation

- **[SKILL.md](./SKILL.md)** - Main skill definition
- **[config/README.md](./config/README.md)** - Configuration guide (optional)

## License

MIT License - See repository LICENSE for details.
