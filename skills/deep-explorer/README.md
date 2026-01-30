---
name: deep-explorer
description: Git-based codebase exploration with delta analysis. Performs full exploration on first run, then incremental delta exploration tracking committed and uncommitted changes.
location: managed
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git *)
  - Bash(ls *)
  - Bash(find *)
  - Bash(jq *)
  - Task
  - Write
  - Bash(mkdir *)
---

# Deep Explorer

Git-based codebase exploration framework with intelligent delta analysis.

## Overview

Deep Explorer helps you understand how a codebase works by analyzing its structure, architecture, patterns, and workflows. It uses Git to efficiently track changes between explorations, performing full analysis on first run and incremental delta analysis on subsequent runs.

**Key insight:** Instead of re-exploring the entire codebase every time, Deep Explorer uses Git to detect what changed and only re-explores those areas.

## Key Features

- **Parallel Sub-Agent Execution:** Spawns multiple explorer agents for faster analysis
- **Git-Based Delta Tracking:** Efficiently tracks changes using Git as reference
- **Full + Delta Exploration:** Complete analysis first run, incremental updates after
- **Uncommitted Change Detection:** Analyzes both committed and work-in-progress files
- **Architecture Analysis:** Identifies patterns, structures, and design principles
- **Dependency Mapping:** Traces relationships between components
- **Impact Analysis:** Shows what's affected by changes
- **No Git Pollution:** Doesn't commit exploration reports to Git
- **Flexible:** Works with dirty working directory
- **Scalable:** Handles large codebases efficiently with parallel execution

## Quick Start

```bash
# Install the skill
cp -r skills/deep-explorer ~/.claude/skills/

# First run - full exploration
/deep-explorer
# → Generates full codebase exploration report
# → Establishes baseline for future delta explorations

# Make some code changes...
# (commit some, leave some uncommitted)

# Second run - delta exploration
/deep-explorer
# → Detects changes using Git
# → Re-explores only changed areas
# → Generates delta report showing what changed
```

## Parallel Execution Architecture

Deep Explorer uses parallel sub-agents to speed up analysis:

### Full Exploration: 5 Parallel Agents

```
Spawn in parallel:
├── Structure Explorer (30%) - Directory hierarchy, file distribution
├── Technology Explorer (20%) - Languages, frameworks, dependencies
├── Architecture Explorer (25%) - Patterns, design, organization
├── Workflow Explorer (15%) - Entry points, data flows
└── Dependency Explorer (10%) - Component relationships

Each agent runs independently
Results aggregated into comprehensive report
```

**Performance:** ~5x faster than sequential analysis

### Delta Exploration: N Parallel Agents

```
Changed files grouped by directory:
├── src/auth/ (3 files) → File Analyzer Agent #1
├── src/api/ (2 files) → File Analyzer Agent #2
└── src/config/ (1 file) → File Analyzer Agent #3

Each agent analyzes its assigned files
Results aggregated into delta report
```

**Performance:** Scales with number of changed files

---

## How It Works

### First Run: Full Exploration

```
User: "/deep-explorer"

→ No previous baseline found
→ Exploration Type: FULL

Analyzes:
├── Repository structure
├── Technology stack
├── Architecture patterns
├── Code workflows
├── Component relationships
└── Configuration

Generates:
├── Comprehensive exploration report
└── Baseline metadata (commit: abc123)

Saves to:
└── .outputs/exploration/20260130-143000-exploration-full.md
```

### Subsequent Runs: Delta Exploration

```
User: "/deep-explorer"
(After making changes to src/auth/ and src/api/)

→ Previous baseline found (commit: abc123)
→ Exploration Type: DELTA

Detects changes:
├── Committed: src/auth/oauth2.ts (added)
├── Committed: src/legacy/old-auth.ts (deleted)
└── Uncommitted: src/api/routes.ts (modified) ⚠️

Re-explores:
├── Only the 3 changed files
└── Traces impact on related components

Generates:
├── Delta report showing changes
├── Impact analysis
└── New baseline (commit: def456)

Saves to:
└── .outputs/exploration/20260130-164500-exploration-delta.md
```

## Use Cases

### 1. **Onboarding to Unfamiliar Codebase**

```
Scenario: New developer joins team
Action: Run /deep-explorer
Result: Comprehensive understanding of:
  - Project structure
  - Technology stack
  - Architecture patterns
  - Key workflows
  - How everything connects
```

### 2. **Understanding Feature Implementation**

```
Scenario: Need to modify authentication system
Action: Run /deep-explorer
Result: Detailed exploration of:
  - Auth-related files
  - Dependencies and relationships
  - Data flow
  - Integration points
```

### 3. **Tracking Code Evolution**

```
Scenario: Want to understand what changed in last sprint
Action: Run /deep-explorer (after previous baseline)
Result: Delta report showing:
  - What files changed
  - New components added
  - Removed components
  - Impact on system architecture
```

### 4. **Pre-Refactoring Analysis**

```
Scenario: Planning major refactoring
Action: Run /deep-explorer
Result: Current state documentation:
  - What exists today
  - How components relate
  - Dependencies to preserve
  - Baseline for before/after comparison
```

### 5. **Documentation Generation**

```
Scenario: Need to document codebase
Action: Run /deep-explorer
Result: Comprehensive documentation of:
  - Architecture
  - Patterns
  - Workflows
  - Component relationships
```

## Exploration Types

### Full Exploration

**When:** First run, no previous baseline

**Analyzes:**
- Complete directory structure
- All files in repository
- Technology stack inventory
- Architecture patterns
- Design patterns
- Code workflows
- Component dependencies
- Configuration

**Output:** Comprehensive baseline report

### Delta Exploration

**When:** Subsequent runs, baseline exists

**Analyzes:**
- Git diff: baseline → HEAD (committed changes)
- Git status: working directory (uncommitted changes)
- Only re-explores changed files
- Traces impact on unchanged files

**Output:** Delta report showing changes and impact

## Change Detection

Deep Explorer uses Git to detect three types of changes:

### 1. Committed Changes (Stable ✅)

```bash
# What changed between baseline and current commit
git diff <baseline> HEAD

Examples:
✅ src/auth/oauth2.ts (added, committed)
✅ src/middleware/rate-limit.ts (added, committed)
✅ src/legacy/old-auth.ts (deleted, committed)
```

**Status:** Stable, committed to Git, unlikely to change

### 2. Uncommitted Changes (Work in Progress ⚠️)

```bash
# Working directory modifications
git diff HEAD

# Staged but not committed
git diff --cached

Examples:
⚠️  src/api/routes.ts (modified, not committed)
⚠️  src/utils/helpers.ts (staged, not committed)
```

**Status:** Work in progress, may still change

### 3. Untracked Files (New ⚠️)

```bash
# New files not in Git
git ls-files --others --exclude-standard

Examples:
⚠️  src/new-feature.ts (not tracked)
⚠️  tests/new-test.spec.ts (not tracked)
```

**Status:** New additions, not yet in Git

## Output Format

### Directory Structure

```
.outputs/exploration/
├── 20260125-103000-exploration-full.md       # First full exploration
├── 20260125-103000-exploration-full.json     # Metadata
├── 20260130-164500-exploration-delta.md      # Delta exploration
├── 20260130-164500-exploration-delta.json    # Metadata
├── latest-exploration.md → (symlink)          # Most recent report
└── latest-exploration.json → (symlink)        # Most recent metadata
```

### Full Exploration Report Sections

1. **Repository Structure** - Directory hierarchy, file distribution
2. **Technology Stack** - Languages, frameworks, tools, dependencies
3. **Architecture Analysis** - Patterns, structure, design
4. **Entry Points & Workflows** - How the application runs
5. **Component Relationships** - Dependencies and coupling
6. **Configuration** - Environment variables, config files
7. **Testing Strategy** - Test organization and coverage
8. **Baseline Metadata** - For future delta explorations

### Delta Exploration Report Sections

1. **Change Summary** - Overview of what changed
2. **Committed Changes** - Stable changes (✅)
3. **Uncommitted Changes** - Work in progress (⚠️)
4. **Architecture Changes** - Patterns added/removed
5. **Impact Analysis** - What's affected by changes
6. **Dependency Changes** - New/removed dependencies
7. **Recommendations** - Suggested next steps
8. **Next Baseline** - Updated baseline for next run

## Git Requirements

### Prerequisites

```bash
# 1. Must be a Git repository
git init

# 2. Must have at least one commit
git add .
git commit -m "Initial commit"

# Now deep-explorer will work
/deep-explorer
```

### What Git Is Used For

✅ **Git is used for:**
- Detecting changes between explorations
- Finding committed vs uncommitted changes
- Tracking baseline commit reference
- Identifying new/modified/deleted files

❌ **Git is NOT used for:**
- Committing exploration reports
- Forcing user to commit changes
- Requiring clean working directory
- Storing exploration history

### Works With

- ✅ Uncommitted changes in working directory
- ✅ Staged but not committed changes
- ✅ Untracked new files
- ✅ Mixed committed/uncommitted state
- ✅ Dirty working directory

## Configuration (Optional)

Most projects work with defaults, but you can customize:

### Config File

```yaml
# .outputs/exploration/config.yaml

exploration:
  # What to include
  include_uncommitted: true
  max_file_size: 1048576  # 1MB per file

  # What to ignore
  ignore_patterns:
    - "node_modules/**"
    - "*.lock"
    - "dist/**"
    - "build/**"
    - ".git/**"

  # Analysis depth
  trace_dependencies: true
  analyze_imports: true
  detect_patterns: true

  # Output options
  include_code_samples: false
  max_sample_lines: 10
```

### Environment Variables

```bash
export DEEP_EXPLORER_OUTPUT_DIR=".outputs/exploration/"
export DEEP_EXPLORER_INCLUDE_UNCOMMITTED="true"
export DEEP_EXPLORER_MAX_FILE_SIZE="1048576"
```

## Example Workflow

### Starting a New Project

```bash
# Day 1: Initial exploration
/deep-explorer
# → Full exploration
# → Baseline: commit abc123
# → Report: Complete codebase analysis

# Week 1: After adding authentication
/deep-explorer
# → Delta exploration
# → Detects: 5 new files in src/auth/
# → Report: What was added + impact

# Week 2: After refactoring
/deep-explorer
# → Delta exploration
# → Detects: 12 modified files, 3 deleted
# → Report: What changed + architecture updates

# Week 3: Mid-development
/deep-explorer
# → Delta exploration
# → Detects: 2 committed + 3 uncommitted files
# → Report: Stable changes + work in progress
```

## Benefits

### Efficiency

- ✅ First run: Full analysis (one time cost)
- ✅ Subsequent runs: Only analyze changed areas (fast)
- ✅ No redundant re-exploration of unchanged code
- ✅ Scales to large codebases

### Accuracy

- ✅ Git-based change detection (reliable)
- ✅ Differentiates stable vs work-in-progress
- ✅ Tracks actual code changes, not timestamps
- ✅ Identifies impact of changes

### Flexibility

- ✅ Works with uncommitted changes
- ✅ No forced Git commits
- ✅ Accepts dirty working directory
- ✅ No Git pollution from exploration reports

### Documentation

- ✅ Persistent exploration history
- ✅ Reusable reference documentation
- ✅ Delta reports show evolution
- ✅ Baseline for before/after comparison

## Common Scenarios

### Scenario: "I just cloned this repo, what is it?"

```bash
/deep-explorer
```

**Result:** Full exploration report explaining:
- What the project does
- How it's organized
- What technologies it uses
- How everything connects

### Scenario: "What changed since last week?"

```bash
/deep-explorer
```

**Result:** Delta report showing:
- Committed changes (what's done)
- Uncommitted changes (what's in progress)
- Impact analysis (what's affected)
- Architecture changes

### Scenario: "I need to modify the auth system"

```bash
/deep-explorer
```

**Result:** Exploration of:
- Current auth implementation
- Related components
- Dependencies
- Integration points

### Scenario: "Planning a refactoring"

```bash
# Before refactoring
/deep-explorer
# → Baseline: Current state

# (Do refactoring work...)

# After refactoring
/deep-explorer
# → Delta: What changed + impact
```

## Troubleshooting

### "ERROR: deep-explorer requires a Git repository"

**Cause:** Not in a Git repository

**Solution:**
```bash
git init
git add .
git commit -m "Initial commit"
```

### "ERROR: No commits in repository"

**Cause:** Git repo exists but no commits

**Solution:**
```bash
git add .
git commit -m "Initial commit"
```

### "No changes detected"

**Cause:** Nothing changed since last exploration

**Result:** Delta report will show "No changes detected"

### Large number of uncommitted files

**Not an error:** Delta exploration includes uncommitted files by design

**To exclude:** Set `include_uncommitted: false` in config

## Best Practices

### When to Run

- ✅ Starting work on unfamiliar code
- ✅ After major feature development
- ✅ Before major refactoring
- ✅ When onboarding new developers
- ✅ Periodically (weekly/monthly)

### When NOT to Run

- ❌ After every single commit (too frequent)
- ❌ During active development (wait for logical checkpoint)
- ❌ On non-Git repositories (won't work)

### Recommended Workflow

1. **Initial Setup:** Run full exploration, review baseline
2. **Regular Checkpoints:** Run delta exploration weekly/monthly
3. **Before Refactoring:** Run exploration to document current state
4. **After Major Changes:** Run delta to understand impact
5. **For Documentation:** Use exploration reports as reference

## Documentation

- **[SKILL.md](./SKILL.md)** - Technical implementation
- **[schemas/](./schemas/)** - Output format specifications
- **[examples/](./examples/)** - Example exploration reports

## License

MIT License - See repository LICENSE for details.
