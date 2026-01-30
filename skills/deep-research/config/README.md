# Deep Research Configuration Guide

This guide explains configuration options for Deep Research.

**Important:** Deep Research is designed to be **conversation-driven**. Most of the time, you don't need to configure anything - the skill will intelligently extract research intent, detect domains, and allocate effort based on your conversation context.

Configuration is **optional** and primarily for:
- Adjusting effort allocation for your research needs
- Customizing execution parameters
- Fine-tuning output format

## Configuration Files

Configuration files (if needed) go in a generic output directory:

```
.outputs/research/
├── config.yaml              # Main configuration (optional)
└── weights.yaml             # Domain weights (optional)
```

**Configurable** via environment variable:

```bash
export DEEP_RESEARCH_CONFIG_DIR=".outputs/research/"
```

## config.yaml (Optional)

Main configuration for Deep Research behavior.

### Full Reference

```yaml
# .outputs/research/config.yaml

# Effort Allocation
effort_distribution:
  primary_domains: 0.70      # Effort for explicitly mentioned domains
  secondary_domains: 0.30    # Effort for inferred domains

# Query Generation
queries_per_domain:
  primary: 8-10              # Queries for primary domains
  secondary: 4-6             # Queries for secondary domains

# Execution
research:
  parallel_execution: true   # Run researchers in parallel
  max_concurrent_researchers: 10  # Max concurrent researchers
  timeout_seconds: 300       # Per-researcher timeout

# Tool Detection
auto_detect_tools: true      # Auto-detect available MCP tools
tool_fallback: "graceful"    # graceful | strict (fail if tools missing)

# Output
output_format: "markdown"    # markdown | json | html
include_json: true           # Generate JSON version
show_research_progress: true # Show real-time progress
```

### Minimal Configuration

```yaml
# .outputs/research/config.yaml (minimal)

effort_distribution:
  primary_domains: 0.70
  secondary_domains: 0.30

parallel_execution: true
```

## Domain Weights (Optional)

Configure how research effort is allocated across detected domains.

### Default Weights

```yaml
# .outputs/research/weights.yaml

effort_distribution:
  # Primary vs Secondary allocation
  primary_domains: 0.70      # 70% to explicitly mentioned domains
  secondary_domains: 0.30    # 30% to contextually inferred domains

queries_per_domain:
  primary: 8-10              # Queries for primary domains
  secondary: 4-6             # Queries for secondary domains
```

### Per-Domain Weights (Optional)

```yaml
# .outputs/research/weights.yaml

domain_weights:
  # Override default allocation for specific domains
  # The system will automatically apply these when domains are detected

  architecture:
    weight: 1.2              # 20% more effort than default
    priority: HIGH

  security:
    weight: 1.0              # Standard effort
    priority: HIGH

  performance:
    weight: 0.8              # 20% less effort than default
    priority: MEDIUM

  # Add any domain - system is domain-agnostic
```

### Query Intensity Profiles

```yaml
# .outputs/research/weights.yaml

query_profiles:
  # Predefined query intensity patterns
  comprehensive:
    primary_queries: 12-15
    secondary_queries: 6-8

  standard:
    primary_queries: 8-10
    secondary_queries: 4-6

  focused:
    primary_queries: 5-7
    secondary_queries: 2-3

  quick:
    primary_queries: 3-5
    secondary_queries: 1-2
```

## Environment Variables

Override configuration with environment variables:

```bash
# Effort allocation
export DEEP_RESEARCH_PRIMARY_RATIO="0.70"
export DEEP_RESEARCH_SECONDARY_RATIO="0.30"

# Query generation
export DEEP_RESEARCH_PRIMARY_QUERIES="8-10"
export DEEP_RESEARCH_SECONDARY_QUERIES="4-6"

# Execution
export DEEP_RESEARCH_PARALLEL="true"
export DEEP_RESEARCH_MAX_CONCURRENT="10"
export DEEP_RESEARCH_TIMEOUT="300"

# Tool handling
export DEEP_RESEARCH_AUTO_DETECT_TOOLS="true"
export DEEP_RESEARCH_TOOL_FALLBACK="graceful"

# Output
export DEEP_RESEARCH_OUTPUT_FORMAT="markdown"
export DEEP_RESEARCH_INCLUDE_JSON="true"
export DEEP_RESEARCH_SHOW_PROGRESS="true"

# Output directory
export DEEP_RESEARCH_OUTPUT_DIR=".outputs/research/"

# Configuration directory
export DEEP_RESEARCH_CONFIG_DIR=".outputs/research/"
export DEEP_RESEARCH_CONFIG_FILE="config.yaml"
```

## Configuration Priority

Configuration is applied in this order (later overrides earlier):

1. Built-in defaults
2. Environment variables
3. `config.yaml`
4. `weights.yaml`
5. Command-line arguments

## Research Depth Configuration

Control research depth based on your needs:

```yaml
# .outputs/research/config.yaml

research_depth_profiles:
  comprehensive:
    primary_queries: 12-15
    secondary_queries: 6-8
    validation_layers: 3      # All three validation layers
    cross_domain_analysis: full

  standard:
    primary_queries: 8-10
    secondary_queries: 4-6
    validation_layers: 2      # Credibility + cross-reference
    cross_domain_analysis: standard

  quick:
    primary_queries: 3-5
    secondary_queries: 1-2
    validation_layers: 1      # Credibility only
    cross_domain_analysis: minimal
```

**Select depth via environment:**
```bash
export DEEP_RESEARCH_DEPTH="standard"  # or comprehensive, quick
```

## Tool Configuration

Deep Research auto-detects available MCP tools. You can customize tool behavior:

```yaml
# .outputs/research/config.yaml

tool_configuration:
  # Search tools
  search_tools:
    - mcp__brave-search__brave_web_search
    - mcp__web-search-prime__webSearchPrime

  # Content extraction
  reader_tools:
    - mcp__web-reader__webReader

  # Documentation queries
  doc_tools:
    - mcp__context7__query-docs
    - mcp__zread__search_doc

  # Validation
  validation_tools:
    - mcp__sequential-thinking__sequentialthinking

  # Fallback behavior
  fallback_strategy: "graceful"  # graceful | strict
```

**Tool Fallback Modes:**
- **graceful**: Continue with available tools, degrade functionality
- **strict**: Fail if required tools are missing

## Output Customization

Customize report format and content:

```yaml
# .outputs/research/config.yaml

output_configuration:
  format: "markdown"           # markdown | json | html
  include_json: true           # Also generate JSON version
  include_appendix: true       # Include methodology section

  sections:
    - executive_summary
    - research_intent
    - findings_by_domain
    - cross_domain_insights
    - synthesis_patterns
    - recommendations
    - quality_assessment
    - sources_bibliography
    - appendix_methodology

  # Source display
  sources:
    show_credibility: true
    show_date: true
    show_type: true
    group_by_domain: true
```

## Validation Configuration

Control the three-layer validation strategy:

```yaml
# .outputs/research/config.yaml

validation_configuration:
  # Layer 1: Source Credibility
  credibility_assessment: true
  credibility_levels:
    - HIGH     # Academic, official docs
    - MEDIUM   # Industry blogs, tutorials
    - LOW      # Personal blogs, forums

  # Layer 2: Cross-Reference Validation
  cross_reference_validation: true
  triangulation_threshold: 3    # Require 3+ sources

  # Layer 3: Internal Consistency
  consistency_check: true
  use_sequential_thinking: true

  # Validation reporting
  show_validation_status: true
  highlight_unvalidated: true
```

## Examples

See [`config/examples/`](./examples/) for complete configuration examples:

- [config/examples/basic-config.yaml](./examples/basic-config.yaml) - Basic setup
- [config/examples/research-focus.yaml](./examples/research-focus.yaml) - Depth vs breadth tuning
- [config/examples/domain-weights.yaml](./examples/domain-weights.yaml) - Per-domain allocation

## Why Configuration is Optional

Deep Research is designed to **just work** by analyzing your conversation:

```
Conversation → Intent Extraction → Domain Detection → Research Plan → Execution → Report
```

No need to:
- ❌ Specify domains manually
- ❌ Configure search queries
- ❌ Set up research parameters
- ❌ Define output formats
- ❌ Configure tool availability

Just:
- ✅ State your research topic naturally
- ✅ Invoke /deep-research
- ✅ Get comprehensive research report

Configuration is **optional** and only needed when you want to:
- Adjust effort allocation
- Customize execution parameters
- Fine-tune output format
- Modify validation strategy

## Troubleshooting

### Research is too shallow

Increase query count:

```yaml
queries_per_domain:
  primary: 12-15
  secondary: 6-8
```

### Research takes too long

Reduce concurrent researchers or queries:

```yaml
research:
  max_concurrent_researchers: 5

queries_per_domain:
  primary: 5-7
  secondary: 2-3
```

### Missing tools detected

The system will gracefully degrade. To see what's available:

```bash
# Check available tools
export DEEP_RESEARCH_SHOW_PROGRESS="true"
```

### Reports too verbose

Simplify output:

```yaml
output_configuration:
  sections:
    - executive_summary
    - findings_by_domain
    - recommendations

  include_appendix: false
  include_json: false
```
