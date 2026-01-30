# Deep Research

Generic multi-domain research framework with domain-aware scheduling.

## Overview

Deep Research is a model-agnostic, **domain-agnostic** research framework that performs comprehensive research on **any topic** using intelligent domain detection and parallel information gathering.

It works for:
- **Technical:** Architecture, frameworks, best practices, implementation strategies
- **Business:** Market research, competitive analysis, industry trends
- **Academic:** Literature reviews, theoretical foundations, state-of-the-art
- **Cross-Domain:** Topics spanning multiple fields (e.g., "AI regulation business impact")
- **Any topic** - fully dynamic and domain-agnostic

## Key Features

- **Conversation-Driven:** Extracts research intent from what you discuss
- **Model-Agnostic:** Works with any available AI model (no hardcoded names)
- **Domain-Agnostic:** Dynamically adapts to ANY domain or topic
- **Tool Discovery:** Automatically detects available MCP tools and adapts research strategy
- **Multi-Method Research:** Web search, browser automation, and interactive crawling
- **Domain-Aware Scheduling:** Allocates research effort based on domain relevance
- **Parallel Research:** Executes multiple domain researchers simultaneously
- **Browser Automation:** Handles dynamic content, interactive sites, and complex workflows
- **Evidence-Based:** All findings tied to credible, clickable source URLs with validation
- **Cross-Domain Insights:** Identifies emergent insights from domain intersections
- **Standardized Output:** Format validation with source quality enforcement
- **No Configuration Required:** Works out of the box

## Quick Start

```bash
# Install the skill
cp -r skills/deep-research .claude/skills/

# Use the skill - just state your research topic naturally
User: "I need to research event sourcing with Kafka"
/deep-research

# The skill automatically detects domains and generates
# a comprehensive research report
```

## How It Works

### 1. You State Your Research Topic

```
User: "Research how to implement event sourcing with Kafka.
      I'm concerned about performance and data consistency."
```

### 2. Deep Research Analyzes

Extracts from conversation:
- **Primary Topic:** Event sourcing with Kafka
- **Primary Domains:** Software Architecture, Distributed Systems
- **Secondary Domains:** Performance Engineering, Data Consistency
- **Research Depth:** Standard (implementation-focused)

### 3. Research Plan Is Generated

```
Primary Domains (70% effort):
  - Software Architecture: 8-10 queries
  - Distributed Systems: 8-10 queries

Secondary Domains (30% effort):
  - Performance Engineering: 4-6 queries
  - Data Consistency: 4-6 queries
```

### 4. Parallel Research Executes

```
✓ Architecture Researcher (8 queries)
✓ Distributed Systems Researcher (8 queries)
✓ Performance Researcher (5 queries)
✓ Consistency Researcher (5 queries)
✓ Cross-Domain Analyst (intersections)
```

### 5. Report Is Generated

Comprehensive research report with:
- Key findings by domain with evidence
- Cross-domain insights
- Synthesis of patterns and debates
- Evidence-based recommendations
- Source bibliography with credibility assessment

## Conversation Examples

### Example 1: Technical Research

```
User: "Research event sourcing with Kafka for a microservices
      architecture. Need to understand performance implications."

/deep-research

→ Detects: Architecture (primary), Distributed Systems (primary)
→ Detects: Performance (secondary), Microservices (secondary)
→ Returns: Technical research with architecture + performance focus
```

### Example 2: Business Research

```
User: "I need to understand the business implications of AI regulation
      in the EU for our SaaS product."

/deep-research

→ Detects: Business (primary), Law/Regulation (primary)
→ Detects: SaaS (secondary), Ethics (secondary)
→ Returns: Business + legal research with practical implications
```

### Example 3: Cross-Domain Research

```
User: "Research the intersection of privacy, security, and user experience
      in authentication systems for fintech applications."

/deep-research

→ Detects: Security (primary), UX Design (primary), Privacy (primary)
→ Detects: Fintech (secondary), Compliance (secondary)
→ Returns: Multi-domain research with intersection analysis
```

### Example 4: Academic/Literature Review

```
User: "What's the current state of research on transformer model
      interpretability? Need both technical and philosophical perspectives."

/deep-research

→ Detects: Machine Learning (primary), Philosophy of AI (primary)
→ Detects: Research Methods (secondary)
→ Returns: Academic-style review with technical + philosophical synthesis
```

## Research Phases

### Phase 1: Intent Analysis & Domain Detection

Extract from conversation:
- Primary research topic
- Explicitly mentioned domains
- Inferred domains from context
- Research depth indicators

**Example Output:**
```yaml
primary_domains:
  - domain: "Software Architecture"
    confidence: HIGH
    keywords: ["event sourcing", "architecture"]

secondary_domains:
  - domain: "Performance"
    confidence: MEDIUM
    keywords: ["performance", "optimization"]
```

### Phase 2: Research Planning

Generate domain-aware research plan:
- 70% effort to primary domains (8-10 queries each)
- 30% effort to secondary domains (4-6 queries each)
- Multiple query types: overview, technical, practical, critical

**Example Plan:**
```yaml
Software Architecture (70%):
  - "event sourcing architecture overview"
  - "event sourcing implementation patterns"
  - "event sourcing vs traditional databases"
  - ... (8 total queries)

Performance (30%):
  - "event sourcing performance optimization"
  - "event sourcing scalability challenges"
  - ... (5 total queries)
```

### Phase 3: Information Gathering

Execute parallel research with multi-method approach:
- Discover available research tools automatically
- Spawn domain researchers in parallel
- Adapt research method to content type
- Extract findings with clickable source URLs
- Assess source credibility

**Research Methods:**

**Standard Web Research:**
- WebSearch (Brave Search, WebSearchPrime)
- Web Reader (content extraction)
- Documentation Query (for technical topics)

**Dynamic Content:**
- Playwright browser automation for JavaScript-heavy sites
- Browser snapshot capture for dynamic loading
- JavaScript evaluation for data extraction

**Interactive Research:**
- Form filling and search interfaces
- Multi-step navigation workflows
- Paginated result extraction
- Agent-browser skill for complex interactions

**Tool Selection Logic:**
```
Static content → web-reader
Dynamic content → Playwright automation
Complex interaction → agent-browser skill
Fallback gracefully if tools unavailable
```

### Phase 4: Cross-Domain Analysis

Explore intersections:
- Where domains agree
- Where domains conflict
- Emergent insights from intersections

**Example:**
```
Architecture + Performance Intersection:
  Agreement: Event sourcing enables better scalability
  Tension: Performance vs. consistency trade-offs
  Insight: CQRS pattern can mitigate read performance issues
```

### Phase 5: Analysis & Synthesis

Three-layer validation:
1. **Source Credibility:** HIGH/MEDIUM/LOW assessment
2. **Cross-Reference:** Triangulate findings across sources
3. **Consistency Check:** Validate logical coherence

### Phase 6: Recommendations & Reporting

Generate structured report:
- Executive summary
- Key findings by domain
- Cross-domain insights
- Evidence-based recommendations
- Source bibliography

## Domain Detection

### How Domains Are Detected

**Primary Domains (70% effort):**
- Explicitly mentioned topics
- Direct subject areas
- Named fields of study

**Secondary Domains (30% effort):**
- Contextually inferred
- Related concerns
- Implicit connections

### Domain Detection Examples

| Conversation | Primary Domains | Secondary Domains |
|-------------|----------------|-------------------|
| "event sourcing with Kafka" | Software Architecture, Distributed Systems | Performance, Data Consistency |
| "AI regulation business impact" | Business, Law/Regulation | Ethics, Technology |
| "privacy vs. security in UX" | Security, UX Design, Privacy | Compliance, User Trust |

Any domain can be detected - the system analyzes conversation naturally.

## Browser Automation & Web Crawling

Deep Research includes advanced browser automation capabilities for handling modern web content.

### When Browser Automation is Used

**Automatic Detection:**
The skill automatically uses browser automation when:
- ❌ Standard web-reader returns incomplete content
- ❌ JavaScript is required to view content
- ❌ Dynamic content doesn't load without interaction
- ❌ Search interfaces require form submission
- ❌ Paginated results need navigation

### Research Method Selection

```
┌─────────────────────────────────────────┐
│ Content Type Detection                  │
└─────────────────────────────────────────┘
              ↓
    ┌─────────┴─────────┐
    │                   │
Static HTML        Dynamic/Interactive
    │                   │
web-reader     Browser Automation
    │                   │
    ↓                   ↓
Extract with      Playwright Tools
URLs              + agent-browser
```

### Browser Automation Capabilities

**Playwright Tools:**
- `browser_navigate` - Navigate to URLs
- `browser_snapshot` - Capture page state (HTML, text, accessibility tree)
- `browser_click` - Interact with page elements
- `browser_fill_form` - Fill search forms and inputs
- `browser_evaluate` - Execute JavaScript for data extraction
- `browser_take_screenshot` - Visual capture for analysis

**Agent-Browser Skill:**
- Complex multi-step workflows
- Login flows (with proper authorization)
- Human-like interaction timing
- Form filling and submission
- Screenshot capture with AI analysis

### Use Cases

**Dynamic Content Sites:**
```
Example: React/Vue/Angular SPAs
Method: Playwright browser_snapshot
Result: Full rendered HTML with data
```

**Search Interfaces:**
```
Example: Research databases, catalogs
Method: browser_fill_form + browser_click
Result: Extracted search results with URLs
```

**Paginated Results:**
```
Example: Multi-page reports, archives
Method: Navigate → Extract → Click Next → Repeat
Result: Aggregated data from all pages
```

**Interactive Filters:**
```
Example: Product databases, directory sites
Method: agent-browser skill for complex workflows
Result: Filtered results with proper attribution
```

### URL Capture Requirements

**Critical:** All sources must include clickable URLs pointing to actual content:

✅ **Correct:**
```json
{
  "url": "https://docs.example.com/event-sourcing",
  "title": "Event Sourcing Patterns",
  "method": "browser-automation",
  "credibility": "HIGH"
}
```

❌ **Wrong:**
```json
{
  "url": "https://google.com/search?q=event+sourcing",
  "title": "Search results",
  "method": "web-search"
}
```

**URL Requirements:**
- Must point to actual content (not search results)
- Must be clickable and accessible
- Must be permanent (not session-specific)
- If authentication required, note in findings

### Tool Discovery

The skill automatically discovers available research tools at runtime:

**Step 0: Tool Discovery**
```yaml
1. Search for web search tools → ToolSearch("web search")
2. Search for browser tools → ToolSearch("playwright browser")
3. Search for content extraction → ToolSearch("web reader")
4. Build tool inventory
5. Select best method per source type
```

This ensures the skill works with whatever MCP tools are available in your environment.

### Best Practices

**Performance:**
- Browser automation only when necessary
- Limit concurrent browser sessions (max 3)
- Set reasonable timeouts (30s per page)
- Prefer web-reader for static content

**Ethics & Legal:**
- Respect robots.txt
- Honor rate limiting
- Don't bypass paywalls without authorization
- Note access restrictions in findings

**Quality:**
- Always capture source URLs
- Validate URL accessibility
- Cross-reference findings
- Document research method used

## Model Selection

Deep Research is **model-agnostic** - it doesn't hardcode model names:

| Researcher Type | Preference | Fallback |
|----------------|------------|----------|
| **Domain Research** | High capability | Standard capability |
| **Cross-Domain Analysis** | High capability | Standard capability |
| **Validation** | Highest capability (for consistency checks) | High capability |

The system auto-detects what's available and uses the best option.

## Output

Reports are saved with **strict format validation**:

```
.outputs/research/
├── 20250115-143022-research-event-sourcing-kafka.md
├── 20250115-143022-research-event-sourcing-kafka.json
├── 20250116-091545-research-ai-regulation-business.md
├── 20250116-091545-research-ai-regulation-business.json
└── latest-research.md → (symlink to most recent)
```

**Format Standardization:**

All outputs are validated against formal JSON schemas to ensure:
- ✅ Consistent structure across all runs
- ✅ Standardized enum values (no typos or variations)
- ✅ Required sections always present
- ✅ Source quality thresholds enforced
- ✅ Predictable, parseable format

See `schemas/README.md` for details on format requirements.

**Configurable** via environment variable:

```bash
export DEEP_RESEARCH_OUTPUT_DIR=".outputs/research/"
```

## Report Structure

Each report includes (validated format):

1. **Executive Summary** - 3-5 sentence overview (min 50 chars)
2. **Research Intent & Scope** - What was researched with depth classification
3. **Key Findings by Domain** - Domain-specific findings with evidence and sources
4. **Cross-Domain Insights** - Intersections and tensions
5. **Synthesis & Patterns** - Overall patterns and debates
6. **Recommendations** - Evidence-based recommendations with confidence levels
7. **Quality Assessment** - Validation status, credibility distribution, limitations
8. **Sources Bibliography** - All sources with credibility ratings

## Configuration (Optional)

Most projects don't need configuration. But you can optionally configure:

### Effort Allocation

```yaml
# .outputs/research/config.yaml

effort_distribution:
  primary_domains: 0.70
  secondary_domains: 0.30

queries_per_domain:
  primary: 8-10
  secondary: 4-6
```

### Execution Settings

```yaml
# .outputs/research/config.yaml

research:
  parallel_execution: true
  max_concurrent_researchers: 10
  timeout_seconds: 300
```

### Environment Variables

```bash
# Effort allocation
export DEEP_RESEARCH_PRIMARY_RATIO="0.70"
export DEEP_RESEARCH_SECONDARY_RATIO="0.30"

# Execution
export DEEP_RESEARCH_PARALLEL="true"
export DEEP_RESEARCH_MAX_CONCURRENT="10"

# Output
export DEEP_RESEARCH_OUTPUT_DIR=".outputs/research/"
```

## Why Conversation-Driven?

Traditional research frameworks require:
- ❌ Specifying domains manually
- ❌ Configuring search queries
- ❌ Setting up research parameters
- ❌ Defining output formats

Deep Research just needs:
- ✅ State your research topic naturally
- ✅ Invoke /deep-research
- ✅ Get comprehensive research report

The system extracts everything from your conversation and dynamically generates appropriate research plans.

## Philosophy: Domain-Aware Research

### The Problem: Equal Treatment

Most research tools treat all domains equally:
- Generic search queries
- Same depth for all topics
- No prioritization

### The Solution: Domain-Aware Scheduling

Deep Research allocates effort intelligently:
- **Primary domains** (explicitly mentioned) → 70% effort, 8-10 queries
- **Secondary domains** (contextually inferred) → 30% effort, 4-6 queries

```
User: "Research event sourcing with Kafka"

Equal Treatment:
├── Architecture: 5 queries (same as everything else)
├── Performance: 5 queries (same as everything else)
├── Consistency: 5 queries (same as everything else)
└── Result: Shallow coverage of everything

Domain-Aware:
├── Architecture: 10 queries (primary - 70%)
├── Distributed Systems: 10 queries (primary - 70%)
├── Performance: 5 queries (secondary - 30%)
└── Result: Deep coverage where it matters
```

## Validation Strategy

Three-layer quality assurance:

### Layer 1: Source Credibility
- **HIGH:** Academic papers, official docs, standards bodies
- **MEDIUM:** Industry blogs, tutorials, conference talks
- **LOW:** Personal blogs, forums, unverified claims

### Layer 2: Cross-Reference Validation
Triangulate findings across 3+ independent sources

### Layer 3: Internal Consistency
Use sequential-thinking for logical validation

## Extensibility

The system is fully dynamic:
- **Any domain:** Works for technical, business, academic, creative topics
- **Any model:** Works with Claude, GPT, or any AI system
- **Elastic:** Automatically adapts to what you discuss
- **Tool-agnostic:** Gracefully handles unavailable tools

## Documentation

- **[SKILL.md](./SKILL.md)** - Main skill definition
- **[schemas/README.md](./schemas/README.md)** - Output format specifications
- **[validators/output-validator.md](./validators/output-validator.md)** - Validation logic
- **[config/README.md](./config/README.md)** - Configuration guide (optional)
- **[examples/](./examples/)** - Usage examples

## License

MIT License - See repository LICENSE for details.
