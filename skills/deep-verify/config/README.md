# Deep Verify Configuration Guide

This guide explains configuration options for Deep Verify.

**Important:** Deep Verify is designed to be **conversation-driven**. Most of the time, you don't need to configure anything - the skill will intelligently extract domains and select experts based on your conversation context.

Configuration is **optional** and primarily for:
- Adjusting expert weights for your project's needs
- Customizing output format

## Configuration Files

Configuration files (if needed) go in a generic output directory:

```
.outputs/verification/
├── config.yaml              # Main configuration (optional)
└── weights.yaml             # Expert weights (optional)
```

**Configurable** via environment variable:

```bash
export DEEP_VERIFY_CONFIG_DIR=".outputs/verification/"
```

## config.yaml (Optional)

Main configuration for Deep Verify behavior.

### Full Reference

```yaml
# .outputs/verification/config.yaml

# Model Detection
auto_detect_models: true              # Auto-detect available models
capability_preferences:               # Model capability preference order
  - capability: "highest"             # Use highest capability available
  - capability: "high"                # Use high capability
  - capability: "standard"            # Use standard capability
# Note: No hardcoded model names - system auto-detects what's available

# Execution
parallel_execution: true               # Run experts in parallel
max_parallel_experts: 10              # Max concurrent experts
timeout_seconds: 300                  # Per-expert timeout

# Output
output_format: "markdown"             # markdown | json | html
include_full_prompts: false           # Include expert prompts in output
show_model_selection: true            # Show which capability was used
```

### Minimal Configuration

```yaml
# .outputs/verification/config.yaml (minimal)

auto_detect_models: true
parallel_execution: true
```

## weights.yaml (Optional)

Configure the weight of each expert in the final aggregation.

### Default Weights

```yaml
# .outputs/verification/weights.yaml

weights:
  # Invariant Experts (always run)
  devils_advocate: 0.40      # Biggest shareholder - surfaces hidden risks
  integration: 0.15          # System-wide impact assessment
  third_party: 0.05          # Fresh-eyes perspective

  # Domain Experts (shared pool)
  domain_experts: 0.40       # Total for all domain experts

  # Dynamic Experts (auto-generated)
  dynamic_experts: 0.10      # Per generated expert
```

### Per-Domain Weights (Optional)

```yaml
# .outputs/verification/weights.yaml

weights:
  devils_advocate: 0.40
  integration: 0.15
  third_party: 0.05
  domain_experts: 0.40

  # Optional: Override weights for specific detected domains
  # The system will automatically apply these when domains are detected
  domain_overrides:
    security: 0.20             # Higher weight for security expert
    performance: 0.15          # Higher weight for performance expert
    # ... other domains as detected from conversation
```

## Environment Variables

Override configuration with environment variables:

```bash
# Model selection (capability-based, not model-specific)
export DEEP_VERIFY_AUTO_DETECT_MODELS="true"
export DEEP_VERIFY_FALLBACK_CAPABILITY="standard"

# Execution
export DEEP_VERIFY_PARALLEL="true"
export DEEP_VERIFY_MAX_PARALLEL="10"
export DEEP_VERIFY_TIMEOUT="300"

# Output
export DEEP_VERIFY_OUTPUT_FORMAT="markdown"
export DEEP_VERIFY_SHOW_MODELS="true"

# Output directory
export DEEP_VERIFY_OUTPUT_DIR=".outputs/verification/"

# Configuration directory
export DEEP_VERIFY_CONFIG_DIR=".outputs/verification/"
export DEEP_VERIFY_CONFIG_FILE="config.yaml"
```

## Per-Configuration

Configuration is applied in this order (later overrides earlier):

1. Built-in defaults
2. Environment variables
3. `config.yaml`
4. `weights.yaml`
5. Command-line arguments

## Examples

See [`examples/`](../examples/) for complete configuration examples:

- [examples/basic-config.yaml](../examples/basic-config.yaml) - Basic setup
- [examples/weights.yaml](../examples/weights.yaml) - Default weights

## Why Configuration is Optional

Deep Verify is designed to **just work** by analyzing your conversation:

```
Conversation → Analysis → Expert Selection → Verification
```

No need to:
- ❌ Configure triggers
- ❌ Specify domains
- ❌ Set up keywords
- ❌ Define file patterns
- ❌ Specify model names

Just:
- ✅ Discuss your work naturally
- ✅ Invoke /deep-verify
- ✅ Get relevant expert analysis

Configuration is **optional** and only needed when you want to:
- Adjust expert weights
- Customize output format
