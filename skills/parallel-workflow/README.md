# Parallel Workflow

DAG-based task orchestration for executing complex multi-step workflows with dependencies.

## Overview

Parallel Workflow automatically determines optimal execution order for tasks with dependencies, maximizing parallelism while respecting task order constraints.

**Philosophy:** Execute as much as possible in parallel, but respect dependencies.

## Key Features

- **Dependency-Aware Scheduling:** Automatically computes execution order
- **DAG Construction:** Builds directed acyclic graph from task definitions
- **Wave-Based Execution:** Tasks at same dependency level run in parallel
- **Cycle Detection:** Validates workflow before execution
- **Failure Handling:** Skips dependent tasks when parent fails
- **Progress Tracking:** Real-time execution status
- **Performance Metrics:** Reports speedup from parallelization

## Quick Start

```bash
# Install the skill
cp -r skills/parallel-workflow ~/.claude/skills/

# Define workflow with dependencies
User: "I have tasks with dependencies: task-A and task-B are independent,
      task-C depends on both, task-D depends on task-C"
/parallel-workflow

# → Automatically computes:
#    Wave 1: [task-A, task-B]  (parallel)
#    Wave 2: [task-C]           (after Wave 1)
#    Wave 3: [task-D]           (after Wave 2)
```

## The Problem This Solves

### Without Parallel Workflow

**Sequential execution:**
```
task-1 → task-2 → task-3 → task-4 → task-5 → task-6
├─2s───┼─1s───┼─3s───┼─2s───┼─1s───┼─2s───┤
Total: 11 seconds
```

**Manual parallelization (error-prone):**
```
You have to manually figure out:
- Which tasks can run together?
- Which must wait for others?
- What if a task fails?
- Am I missing dependencies?
```

### With Parallel Workflow

**Automatic optimal execution:**
```yaml
# You define dependencies:
tasks:
  - id: task-1
    depends_on: []
  - id: task-2
    depends_on: []
  - id: task-3
    depends_on: [task-1]
  - id: task-4
    depends_on: [task-2]
  - id: task-5
    depends_on: [task-3, task-4]
  - id: task-6
    depends_on: [task-5]

# Skill computes optimal plan:
Wave 1: [task-1, task-2]  (2s + 1s = 2s with parallelism)
Wave 2: [task-3, task-4]  (3s + 2s = 3s with parallelism)
Wave 3: [task-5]          (1s)
Wave 4: [task-6]          (2s)

Total: 8 seconds (vs 11 sequential)
Speedup: 1.4x
```

## How It Works

### 1. Define Tasks with Dependencies

```yaml
tasks:
  - id: analyze-structure
    description: "Analyze directory structure"
    prompt: "Map out directory structure and file organization"
    depends_on: []  # No dependencies - can run first

  - id: analyze-tech
    description: "Identify technologies"
    prompt: "Identify technologies and frameworks used"
    depends_on: [analyze-structure]  # Needs structure first

  - id: analyze-architecture
    description: "Analyze architecture patterns"
    prompt: "Identify architectural patterns"
    depends_on: [analyze-structure, analyze-tech]  # Needs both
```

### 2. Skill Builds DAG

```
analyze-structure ──┬─→ analyze-tech ──┐
                    │                   ├─→ analyze-architecture
                    └───────────────────┘
```

### 3. Computes Execution Waves

```
Wave 1: [analyze-structure]
Wave 2: [analyze-tech]
Wave 3: [analyze-architecture]
```

### 4. Executes with Parallelism

```
Wave 1:  [analyze-structure]          ← 1 task
            ↓
Wave 2:  [analyze-tech]                ← 1 task
            ↓
Wave 3:  [analyze-architecture]        ← 1 task
```

## Use Cases

### Codebase Exploration

```
Problem: Exploring a codebase has natural dependencies
- Need structure before understanding architecture
- Need dependencies before tracing workflows

Solution: Define exploration tasks with dependencies
Wave 1: Analyze structure
Wave 2: Analyze tech stack, Map dependencies (parallel)
Wave 3: Analyze architecture, Trace workflows (parallel)
Wave 4: Synthesize findings
```

### Multi-Stage Verification

```
Problem: Verification stages have dependencies
- Integration check needs domain analysis first
- Final review needs all previous analysis

Solution: Layer verification tasks
Wave 1: Security analysis, Performance analysis (parallel)
Wave 2: Integration check, Devils advocate (parallel, need Wave 1)
Wave 3: Third-party review (needs everything)
```

### Build and Deploy Pipeline

```
Problem: Build pipeline has complex dependencies
- Tests need build to complete
- Deploy needs tests to pass

Solution: Define pipeline stages
Wave 1: Lint, Unit tests (parallel)
Wave 2: Build (needs lint + unit tests)
Wave 3: Integration tests (needs build)
Wave 4: Deploy (needs integration tests)
```

## Task Definition Format

```yaml
tasks:
  - id: "unique-task-id"              # Required: Unique identifier
    description: "What this does"      # Required: Brief description
    prompt: "Detailed instructions"    # Required: Agent instructions
    depends_on: [task-1, task-2]      # Required: Dependencies (empty array if none)
    agent: "agent-type"                # Optional: Specific agent type
    capability: "high"                 # Optional: "highest", "high", "standard"
    timeout: 300000                    # Optional: Timeout in milliseconds
```

**Example:**
```yaml
tasks:
  - id: security-scan
    description: "Run security vulnerability scan"
    prompt: "Analyze code for security vulnerabilities using OWASP standards"
    depends_on: []
    agent: "comprehensive-review:security-auditor"
    capability: "highest"

  - id: deploy
    description: "Deploy to staging"
    prompt: "Deploy application to staging environment"
    depends_on: [security-scan]
    timeout: 600000  # 10 minutes
```

## Execution Waves Explained

### What is a Wave?

A **wave** is a set of tasks that can execute in parallel because they:
1. Have no dependencies on each other
2. Have all their dependencies satisfied by previous waves

### Wave Examples

**Example 1: Simple chain**
```
A → B → C

Wave 1: [A]
Wave 2: [B]
Wave 3: [C]

Parallelization: None (sequential dependencies)
```

**Example 2: Parallel branches**
```
A → C
B → D

Wave 1: [A, B]  (parallel - no dependencies)
Wave 2: [C, D]  (parallel - different branches)

Parallelization: 2x speedup
```

**Example 3: Diamond pattern**
```
    A
   ↙ ↘
  B   C
   ↘ ↙
    D

Wave 1: [A]
Wave 2: [B, C]  (parallel - both need A)
Wave 3: [D]     (needs both B and C)

Parallelization: 1.33x speedup
```

**Example 4: Complex DAG**
```
A → C → E
B → D → F → G

Wave 1: [A, B]        (2 parallel)
Wave 2: [C, D]        (2 parallel)
Wave 3: [E, F]        (2 parallel)
Wave 4: [G]

Parallelization: 1.75x speedup
```

## Failure Handling

### Default: Skip Dependent Tasks

When a task fails, all tasks that depend on it are automatically skipped:

```
Example:
  A → C → E
  B → D

If task C fails:
  ✓ A completed
  ✓ B completed
  ✗ C failed
  ✓ D completed (independent of C)
  ⏭️ E skipped (depends on C which failed)
```

### Execution Report

```markdown
## Execution Summary

**Status:** PARTIAL_FAILURE

**Completed:** 3/5 tasks
**Failed:** 1/5 tasks
**Skipped:** 1/5 tasks

### Failed Tasks

❌ **task-C** (Wave 2)
- Error: "Database connection timeout"
- Impact: Skipped task-E

### Skipped Tasks

⏭️ **task-E** - Skipped because task-C failed
```

## Performance Metrics

### Parallelization Factor

```
Parallelization Factor = Total Work Time / Actual Execution Time

Example:
- Total work time: 20 seconds (sum of all task durations)
- Actual execution time: 8 seconds (with parallelism)
- Parallelization factor: 2.5x speedup
```

### Critical Path

The **critical path** is the longest chain of dependent tasks:

```
Example DAG:
  A(2s) → C(3s) → E(1s)  = 6s critical path
  B(4s) → D(1s)          = 5s

Critical path: A → C → E (6 seconds)
Execution time: 6 seconds (limited by critical path)

Even though B takes 4s, it runs in parallel with A(2s),
so it doesn't increase total time.
```

## Error Detection

### Cycle Detection

```
❌ ERROR: Circular dependency detected!

Dependency cycle found:
  task-A depends on task-B
  task-B depends on task-C
  task-C depends on task-A  ← Creates infinite loop!

Please restructure your dependencies to break the cycle.
```

### Missing Dependency

```
❌ ERROR: Invalid dependency reference!

Task "integration-check" depends on "domain-analysis"
But task "domain-analysis" does not exist.

Available tasks: [security-analysis, performance-analysis, integration-check]

Did you mean: "security-analysis"?
```

## Best Practices

### 1. Minimize Critical Path

Keep the longest dependency chain as short as possible:

```yaml
# ❌ Bad: Long critical path
A → B → C → D → E → F  (6 waves, no parallelism)

# ✅ Good: Short critical path, more parallelism
A → D → F  (3 waves)
B → E
C
```

### 2. Declare Only Necessary Dependencies

Don't over-constrain:

```yaml
# ❌ Bad: Unnecessary dependency
- id: task-C
  depends_on: [task-A, task-B]
  # If task-C only actually needs task-A, this unnecessarily waits for B

# ✅ Good: Minimal dependencies
- id: task-C
  depends_on: [task-A]
  # Only declare actual dependencies
```

### 3. Group Related Tasks

Keep related tasks at the same dependency level:

```yaml
# ✅ Good: Related analysis grouped in same wave
Wave 1:
  - security-analysis
  - performance-analysis
  - accessibility-analysis

Wave 2:
  - synthesis  # Uses all Wave 1 results
```

### 4. Balance Wave Sizes

Avoid waves with very different sizes:

```yaml
# ⚠️ Suboptimal: Unbalanced
Wave 1: [task-1]                    # 1 task
Wave 2: [task-2, ..., task-10]      # 9 tasks
Wave 3: [task-11]                   # 1 task

# ✅ Better: Balanced
Wave 1: [task-1, task-2, task-3]    # 3 tasks
Wave 2: [task-4, task-5, task-6]    # 3 tasks
Wave 3: [task-7, task-8]            # 2 tasks
```

## Output Format

```
.outputs/workflow/
├── 20260130-143000-workflow-execution.md
├── 20260130-143000-workflow-execution.json
└── latest-workflow.md → (symlink)
```

## Example: Codebase Exploration

```yaml
tasks:
  # Wave 1: Base structure (no dependencies)
  - id: structure
    description: "Analyze directory structure"
    prompt: "Map out directory structure and file organization"
    depends_on: []

  # Wave 2: Tech and dependencies (need structure)
  - id: tech-stack
    description: "Identify technologies"
    prompt: "Identify technologies, frameworks, and languages"
    depends_on: [structure]

  - id: dependencies
    description: "Map dependencies"
    prompt: "Analyze package dependencies and imports"
    depends_on: [structure]

  # Wave 3: Architecture and workflows (need structure + tech/deps)
  - id: architecture
    description: "Analyze architecture"
    prompt: "Identify architectural patterns and design decisions"
    depends_on: [structure, tech-stack]

  - id: workflows
    description: "Trace workflows"
    prompt: "Trace request flows and data pipelines"
    depends_on: [structure, dependencies]

  # Wave 4: Synthesis (needs everything)
  - id: synthesis
    description: "Synthesize findings"
    prompt: "Combine all findings into comprehensive report"
    depends_on: [architecture, workflows]
```

**Execution:**
```
Wave 1: [structure]                     (1 task)  - 3s
Wave 2: [tech-stack, dependencies]      (2 tasks) - 4s (parallel)
Wave 3: [architecture, workflows]       (2 tasks) - 5s (parallel)
Wave 4: [synthesis]                     (1 task)  - 2s

Total: 14 seconds
Sequential would be: 3+4+4+5+5+2 = 23 seconds
Speedup: 1.6x
```

## When to Use Parallel Workflow

**Use when:**
- ✅ Multiple tasks with clear dependencies
- ✅ Some tasks can run in parallel
- ✅ Need optimal execution order
- ✅ Want to maximize throughput
- ✅ Complex workflow with many steps

**Don't use when:**
- ❌ Simple sequential workflow (just run in order)
- ❌ All tasks are independent (just run all in parallel)
- ❌ Dependencies are simple and obvious
- ❌ Only 2-3 tasks total

## Documentation

- **[SKILL.md](./SKILL.md)** - Technical implementation
- **[schemas/](./schemas/)** - Output format specifications

## License

MIT License - See repository LICENSE for details.
