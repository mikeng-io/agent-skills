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

# Deep Explorer: Git-Based Codebase Exploration

Execute this skill to explore and understand how a codebase works, using Git to efficiently track changes between explorations.

## Execution Instructions

When invoked, you will:

0. **Verify Git repository** - Ensure codebase is a Git repository
1. **Determine exploration type** - Full (first run) or Delta (incremental)
2. **Detect changes** - Use Git to find what changed since last exploration
3. **Execute exploration** - Explore entire codebase (full) or changed areas (delta)
4. **Generate report** - Comprehensive exploration or delta change report
5. **Save baseline** - Store current commit reference for next exploration

---

## Step 0: Verify Git Repository

Before exploration, verify the codebase is a Git repository:

```bash
# Check if Git repository
if ! git rev-parse --is-inside-work-tree 2>/dev/null; then
  echo "ERROR: deep-explorer requires a Git repository"
  echo "Please initialize Git: git init"
  exit 1
fi

# Verify Git is functional
if ! git rev-parse HEAD 2>/dev/null; then
  echo "ERROR: No commits in repository"
  echo "Please make at least one commit before using deep-explorer"
  exit 1
fi
```

**If Git repository does not exist:**
- Display error message
- Explain that deep-explorer requires Git for delta tracking
- Exit gracefully

---

## Step 1: Determine Exploration Type

Check if previous exploration exists to determine strategy:

```bash
# Check for previous exploration
LAST_EXPLORATION=".outputs/exploration/latest-exploration.json"

if [ -f "$LAST_EXPLORATION" ]; then
  # Previous exploration exists
  EXPLORATION_TYPE="delta"
  BASELINE_COMMIT=$(jq -r '.baseline_commit' "$LAST_EXPLORATION")
  BASELINE_TIMESTAMP=$(jq -r '.baseline_timestamp' "$LAST_EXPLORATION")
else
  # No previous exploration
  EXPLORATION_TYPE="full"
  BASELINE_COMMIT=$(git rev-parse HEAD)
  BASELINE_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi
```

**Exploration Types:**

**FULL Exploration:**
- First run (no baseline)
- Explore entire codebase
- Establish baseline for future delta explorations

**DELTA Exploration:**
- Subsequent runs (baseline exists)
- Detect changes using Git
- Re-explore only changed areas
- Generate delta report with impact analysis

---

## Step 2: Detect Changes (Delta Only)

For delta exploration, use Git to detect all changes:

### Committed Changes
```bash
# Get baseline commit from last exploration
BASELINE=$(jq -r '.baseline_commit' .outputs/exploration/latest-exploration.json)
CURRENT=$(git rev-parse HEAD)

# Find committed changes since baseline
git diff --name-status $BASELINE $CURRENT > committed_changes.txt

# Categorize changes
MODIFIED=$(git diff --name-only --diff-filter=M $BASELINE $CURRENT)
ADDED=$(git diff --name-only --diff-filter=A $BASELINE $CURRENT)
DELETED=$(git diff --name-only --diff-filter=D $BASELINE $CURRENT)
RENAMED=$(git diff --name-only --diff-filter=R $BASELINE $CURRENT)
```

### Uncommitted Changes
```bash
# Working directory changes (modified but not staged)
UNCOMMITTED_MODIFIED=$(git diff --name-only HEAD)

# Staged changes (committed to index but not committed)
STAGED=$(git diff --name-only --cached)

# Untracked files (new files not in Git)
UNTRACKED=$(git ls-files --others --exclude-standard)
```

### Combine All Changes
```yaml
changes_detected:
  committed:
    status: stable
    files:
      - modified: [list from git diff]
      - added: [list from git diff]
      - deleted: [list from git diff]
      - renamed: [list from git diff]

  uncommitted:
    status: work_in_progress
    files:
      - modified: [list from git diff HEAD]
      - staged: [list from git diff --cached]
      - untracked: [list from git ls-files --others]

total_changes: <count>
exploration_scope: [list of unique files to re-explore]
```

**Change Categorization:**
- **Committed changes** → Stable, unlikely to change
- **Uncommitted changes** → Work in progress, may change
- **Untracked files** → New additions, not yet in Git

---

## Step 3: Execute Exploration

### Full Exploration (First Run)

Spawn parallel explorer sub-agents for faster analysis:

**Parallel Execution Strategy:**
```yaml
spawn_in_parallel:
  - Structure Explorer (30% weight)
  - Technology Explorer (20% weight)
  - Architecture Explorer (25% weight)
  - Workflow Explorer (15% weight)
  - Dependency Explorer (10% weight)

execution:
  mode: parallel
  max_concurrent: 5
  capability: high
```

**Explorer Agent Templates:**

#### Structure Explorer Agent
```
Capability: high

You are a STRUCTURE EXPLORER. Analyze the repository structure and organization.

## Your Task
1. Map directory hierarchy using Glob and ls
2. Count files by type (extensions)
3. Identify organizational patterns
4. Find configuration files
5. Analyze naming conventions

## Output Format (JSON)
{
  "agent": "structure-explorer",
  "directory_structure": {
    "total_directories": 24,
    "total_files": 188,
    "hierarchy": "..."
  },
  "file_distribution": {
    "typescript": 145,
    "javascript": 23,
    "json": 12,
    "markdown": 8
  },
  "organizational_patterns": [
    "Feature-based organization",
    "Separation of concerns",
    "Test files colocated with source"
  ],
  "configuration_files": [
    "package.json",
    "tsconfig.json",
    ".eslintrc.js",
    "docker-compose.yml"
  ]
}
```

#### Technology Explorer Agent
```
Capability: high

You are a TECHNOLOGY EXPLORER. Inventory the technology stack.

## Your Task
1. Detect languages from file extensions
2. Identify frameworks from package.json, requirements.txt, etc.
3. Find build tools (Makefile, scripts, etc.)
4. Extract dependencies and versions

## Output Format (JSON)
{
  "agent": "technology-explorer",
  "languages": [
    {"name": "TypeScript", "file_count": 145, "primary": true},
    {"name": "JavaScript", "file_count": 23, "primary": false}
  ],
  "frameworks": [
    {"name": "Express.js", "version": "^4.18.0", "purpose": "web server"},
    {"name": "React", "version": "^18.2.0", "purpose": "frontend"}
  ],
  "build_tools": ["npm", "webpack", "docker"],
  "dependencies": {
    "production": {...},
    "development": {...}
  }
}
```

#### Architecture Explorer Agent
```
Capability: high

You are an ARCHITECTURE EXPLORER. Identify architectural patterns and structure.

## Your Task
1. Analyze project structure (MVC, microservices, etc.)
2. Identify module organization
3. Detect design patterns used
4. Assess separation of concerns

## Output Format (JSON)
{
  "agent": "architecture-explorer",
  "project_structure": "Layered architecture",
  "layers": [
    {"name": "API Layer", "location": "src/api/"},
    {"name": "Business Logic", "location": "src/services/"},
    {"name": "Data Layer", "location": "src/models/"}
  ],
  "design_patterns": [
    {"pattern": "Factory", "location": "src/factories/"},
    {"pattern": "Repository", "location": "src/repositories/"},
    {"pattern": "Dependency Injection", "implementation": "constructor-based"}
  ],
  "separation_quality": "high"
}
```

#### Workflow Explorer Agent
```
Capability: high

You are a WORKFLOW EXPLORER. Trace code flows and entry points.

## Your Task
1. Find entry points (main files)
2. Trace key workflows
3. Map data flow patterns
4. Identify integration points

## Output Format (JSON)
{
  "agent": "workflow-explorer",
  "entry_points": [
    {"file": "src/index.ts", "purpose": "Application bootstrap"}
  ],
  "key_workflows": [
    {
      "name": "User Authentication",
      "flow": [
        "src/api/auth/routes.ts",
        "src/services/auth.service.ts",
        "src/repositories/user.repository.ts",
        "Database"
      ]
    }
  ],
  "data_flow_patterns": ["Request-Response", "Event-driven"],
  "integration_points": ["Database", "External APIs", "Cache"]
}
```

#### Dependency Explorer Agent
```
Capability: high

You are a DEPENDENCY EXPLORER. Map component relationships and dependencies.

## Your Task
1. Analyze import/export patterns
2. Map component dependencies using Grep
3. Identify external dependencies
4. Assess module coupling

## Output Format (JSON)
{
  "agent": "dependency-explorer",
  "import_patterns": {
    "relative_imports": 145,
    "absolute_imports": 23,
    "external_imports": 67
  },
  "component_dependencies": {
    "api/": ["services/", "middleware/", "utils/"],
    "services/": ["repositories/", "models/"]
  },
  "coupling_analysis": {
    "level": "low",
    "circular_dependencies": []
  }
}
```

**Aggregate Results:**

After all explorer agents complete, aggregate their findings into comprehensive report.

### Delta Exploration (Incremental)

Spawn parallel file analyzer sub-agents for each changed file/directory:

**Parallel Execution Strategy:**
```yaml
# Group changes by directory or file
change_groups:
  - src/auth/ (3 files changed)
  - src/api/ (2 files changed)
  - src/config/ (1 file changed)

# Spawn one agent per group
spawn_in_parallel:
  - File Analyzer: src/auth/*
  - File Analyzer: src/api/*
  - File Analyzer: src/config/*

execution:
  mode: parallel
  max_concurrent: 10
  capability: high
```

**File Analyzer Agent Template:**

```
Capability: high

You are a FILE ANALYZER for delta exploration. Analyze changed files and their impact.

## Files to Analyze
{list_of_changed_files_in_this_group}

## Change Types Detected
{committed/uncommitted status for each file}

## Your Task

For each changed file:

1. **Read file content** using Read tool
2. **Analyze change type:**
   - Modified: Compare with previous, identify what changed
   - Added: Document new component
   - Deleted: Note removal and document what it was
   - Renamed: Track move and update references

3. **Trace impact** using Grep:
   - What components depend on this file?
   - What does this file depend on?
   - Are there breaking changes?
   - What tests are affected?

4. **Flag stability:**
   - Committed → ✅ Stable
   - Uncommitted → ⚠️ Work in progress

## Output Format (JSON)
{
  "agent": "file-analyzer-{group}",
  "files_analyzed": [
    {
      "file": "src/auth/oauth2.ts",
      "change_type": "added",
      "stability": "committed",
      "status": "✅ Stable",
      "analysis": {
        "type": "Authentication Module",
        "purpose": "OAuth2 authentication flow",
        "exports": ["OAuth2Strategy", "authenticate()"],
        "imports": ["express", "passport-oauth2"],
        "dependencies": {
          "imports": ["express", "passport"],
          "imported_by": ["src/api/auth/routes.ts"]
        },
        "impact": [
          "Replaces src/legacy/old-auth.ts",
          "Used by src/api/auth/routes.ts",
          "Affects login workflow"
        ],
        "breaking_changes": [
          "Session-based auth no longer supported"
        ],
        "affected_tests": [
          "tests/auth/oauth2.spec.ts (new)",
          "tests/api/auth.spec.ts (modified)"
        ]
      }
    }
  ]
}
```

**Aggregate Results:**

After all file analyzer agents complete, aggregate their findings:
- Combine all file analyses
- Cross-reference impacts
- Identify system-wide changes
- Generate delta report

---

## Step 4: Generate Report

### Full Exploration Report Structure

```markdown
# Full Codebase Exploration Report

**Exploration Type:** Full (baseline)
**Repository:** {repository_name}
**Explored At:** {timestamp}
**Baseline Commit:** {commit_hash}
**Total Files:** {file_count}

---

## Repository Structure

### Directory Hierarchy
```
project/
├── src/
│   ├── api/
│   ├── services/
│   └── utils/
├── tests/
├── config/
└── docs/
```

### File Distribution
- TypeScript: 145 files
- JavaScript: 23 files
- JSON: 12 files
- Markdown: 8 files
- Total: 188 files

---

## Technology Stack

### Languages
- TypeScript (primary)
- JavaScript (configuration)
- Shell scripts (deployment)

### Frameworks & Libraries
- Express.js (web server)
- React (frontend)
- Jest (testing)
- Prettier/ESLint (code quality)

### Build Tools
- npm (package management)
- Webpack (bundling)
- Docker (containerization)

### Dependencies
**Production:**
- express: ^4.18.0
- react: ^18.2.0
- ...

**Development:**
- jest: ^29.0.0
- typescript: ^5.0.0
- ...

---

## Architecture Analysis

### Project Structure
**Pattern:** Layered architecture with clear separation

**Layers:**
1. API Layer (`src/api/`)
2. Business Logic (`src/services/`)
3. Data Layer (`src/models/`)
4. Utilities (`src/utils/`)

### Design Patterns
- Factory Pattern: `src/factories/`
- Repository Pattern: `src/repositories/`
- Dependency Injection: Constructor-based
- Middleware Pattern: `src/middleware/`

---

## Entry Points & Workflows

### Main Entry Point
**File:** `src/index.ts`
**Purpose:** Application bootstrap
**Key Operations:**
1. Load configuration
2. Connect to database
3. Initialize Express app
4. Start server

### Key Workflows

**User Authentication Flow:**
```
src/api/auth/routes.ts
  → src/services/auth.service.ts
  → src/repositories/user.repository.ts
  → Database
```

**API Request Flow:**
```
Express Middleware
  → Rate Limiting
  → Authentication
  → Route Handler
  → Service Layer
  → Repository Layer
  → Response
```

---

## Component Relationships

### Module Dependencies

**api/ depends on:**
- services/
- middleware/
- utils/

**services/ depends on:**
- repositories/
- models/
- utils/

**Coupling Analysis:**
- Low coupling between layers ✅
- Clear dependency direction ✅
- Minimal circular dependencies ✅

---

## Configuration

### Environment Variables
- `PORT`: Server port (default: 3000)
- `DATABASE_URL`: Database connection string
- `JWT_SECRET`: Authentication secret
- `NODE_ENV`: Environment (development/production)

### Config Files
- `package.json`: Dependencies and scripts
- `tsconfig.json`: TypeScript configuration
- `.eslintrc.js`: Linting rules
- `docker-compose.yml`: Container orchestration

---

## Testing Strategy

### Test Organization
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```

### Coverage
- Unit tests: 87%
- Integration tests: 65%
- E2E tests: 12 scenarios

---

## Baseline Metadata

```json
{
  "exploration_type": "full",
  "baseline_commit": "abc123",
  "baseline_timestamp": "2026-01-30T14:30:00Z",
  "repository": "deep-verify",
  "files_analyzed": 188,
  "directories": 24
}
```

This exploration establishes the baseline for future delta explorations.
```

### Delta Exploration Report Structure

```markdown
# Delta Codebase Exploration Report

**Exploration Type:** Delta (incremental)
**Repository:** {repository_name}
**Baseline:** Commit {baseline_commit} ({baseline_date})
**Current:** Commit {current_commit} + uncommitted changes
**Time Span:** {days} days
**Explored At:** {timestamp}

---

## Change Summary

**Git Statistics:**
- {n} files modified (committed)
- {n} files added (committed)
- {n} files deleted (committed)
- {n} files renamed (committed)
- {n} files modified (uncommitted) ⚠️
- {n} files staged (uncommitted) ⚠️
- {n} files untracked (uncommitted) ⚠️

**Total:** {n} files changed

**Affected Areas:**
- `src/auth/` - OAuth2 implementation
- `src/api/` - New endpoints
- `src/config/` - Database changes

---

## Committed Changes (Stable)

### ✅ src/auth/oauth2.ts (Added, Committed)
**Commit:** def456
**Status:** ✅ Committed (stable)
**Type:** Authentication Module
**Purpose:** OAuth2 authentication flow

**Structure:**
```typescript
export class OAuth2Strategy {
  authenticate(): Promise<User>
  refresh(): Promise<Token>
}
```

**Dependencies:**
- Imports: `express`, `passport-oauth2`
- Exports: `OAuth2Strategy`, `authenticate()`

**Impact:**
- Replaces `src/legacy/old-auth.ts`
- Used by `src/api/auth/routes.ts`
- Affects login workflow

---

### ✅ src/middleware/rate-limit.ts (Added, Committed)
**Commit:** def456
**Status:** ✅ Committed (stable)
**Type:** Middleware
**Purpose:** API rate limiting

**Structure:**
```typescript
export const rateLimiter: RateLimitMiddleware
```

**Configuration:**
- Max: 100 requests per 15 minutes
- Applies to all API routes

**Impact:**
- All `/api/*` endpoints now rate-limited
- Frontend may need retry logic

---

### ✅ src/legacy/old-auth.ts (Deleted, Committed)
**Commit:** def456
**Status:** ✅ Committed (stable)
**Type:** Authentication (legacy)
**Reason:** Replaced by OAuth2 module

**Impact:**
- All references migrated to `src/auth/oauth2.ts`
- Session-based auth no longer supported
- Breaking change for old clients

---

## Uncommitted Changes (Work in Progress)

### ⚠️  src/api/routes.ts (Modified, Uncommitted)
**Status:** ⚠️ Work in progress (unstaged)
**Type:** API Routes

**Changes Detected:**
- Added 3 new endpoints
- Integrated rate limiting middleware
- Updated error handling

**Impact:**
- New authentication flow endpoints
- All routes now rate-limited

**Warning:** Changes not committed - may still change

---

### ⚠️  src/utils/helpers.ts (New File, Untracked)
**Status:** ⚠️ Not tracked by Git
**Type:** Utility Functions

**Structure:**
```typescript
export function formatDate(date: Date): string
export function validateEmail(email: string): boolean
```

**Impact:**
- Used by `src/api/routes.ts`
- Not yet in repository

**Warning:** New file not added to Git

---

## Architecture Changes

### New Patterns Introduced
- OAuth2 authentication pattern (committed)
- Middleware-based rate limiting (committed)
- Centralized error handling (uncommitted ⚠️)

### Removed Patterns
- Legacy session-based auth (committed)
- Per-route auth checks (committed)

### Structural Changes
- Added `src/middleware/` directory
- Reorganized `src/auth/` structure
- Removed `src/legacy/` directory

---

## Impact Analysis

### Authentication System
**Status:** ✅ Stable (committed)
**What Changed:** OAuth2 replaces session-based auth

**Affected Components:**
- Login flow (rewritten)
- Session management (removed)
- User model (added OAuth fields)
- API endpoints (new auth middleware)

**Breaking Changes:**
- Old `/login` endpoint removed
- Session cookies no longer used
- API clients must use OAuth2 tokens

---

### API Layer
**Status:** ⚠️ Partially stable (mixed committed/uncommitted)
**What Changed:** Rate limiting + new endpoints

**Stable (Committed):**
- Rate limiting middleware deployed
- Configuration complete

**Unstable (Uncommitted):**
- New endpoints not yet committed
- Error handling still being refined

**Recommendation:** Complete and commit API changes

---

## Dependency Changes

### New Dependencies
- `passport-oauth2` (for OAuth2)
- `express-rate-limit` (for rate limiting)

### Removed Dependencies
- `express-session` (replaced by OAuth2)

---

## Recommendations

**For Committed Changes:**
1. ✅ Review OAuth2 security implementation
2. ✅ Test rate limiting in production
3. ✅ Verify legacy auth removal is complete
4. ✅ Update API documentation

**For Uncommitted Changes:**
1. ⚠️  Complete src/api/routes.ts integration
2. ⚠️  Add src/utils/helpers.ts to Git
3. ⚠️  Commit or stash work in progress
4. ⚠️  Run tests before committing

---

## Next Exploration Baseline

```json
{
  "exploration_type": "delta",
  "baseline_commit": "def456",
  "baseline_timestamp": "2026-01-30T16:45:00Z",
  "previous_baseline": "abc123",
  "changes_analyzed": {
    "committed": 3,
    "uncommitted": 2,
    "total": 5
  }
}
```

Next delta exploration will use commit `def456` as baseline.
```

---

## Step 5: Save Baseline & Report

Save exploration results and update baseline:

```bash
# Create output directory
mkdir -p .outputs/exploration

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Save markdown report
REPORT_FILE=".outputs/exploration/${TIMESTAMP}-exploration-${EXPLORATION_TYPE}.md"
echo "$REPORT_CONTENT" > "$REPORT_FILE"

# Save JSON metadata
JSON_FILE=".outputs/exploration/${TIMESTAMP}-exploration-${EXPLORATION_TYPE}.json"
cat > "$JSON_FILE" <<EOF
{
  "exploration_type": "$EXPLORATION_TYPE",
  "baseline_commit": "$(git rev-parse HEAD)",
  "baseline_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "repository": "$(basename $(git rev-parse --show-toplevel))",
  "files_analyzed": $FILE_COUNT,
  "changes_analyzed": {
    "committed": $COMMITTED_COUNT,
    "uncommitted": $UNCOMMITTED_COUNT,
    "total": $TOTAL_COUNT
  },
  "previous_baseline": "$BASELINE_COMMIT"
}
EOF

# Update symlink to latest exploration
ln -sf "${TIMESTAMP}-exploration-${EXPLORATION_TYPE}.md" .outputs/exploration/latest-exploration.md
ln -sf "${TIMESTAMP}-exploration-${EXPLORATION_TYPE}.json" .outputs/exploration/latest-exploration.json
```

**Output Structure:**
```
.outputs/exploration/
├── 20260125-103000-exploration-full.md
├── 20260125-103000-exploration-full.json
├── 20260130-164500-exploration-delta.md
├── 20260130-164500-exploration-delta.json
├── latest-exploration.md → 20260130-164500-exploration-delta.md
└── latest-exploration.json → 20260130-164500-exploration-delta.json
```

---

## Configuration (Optional)

Default configuration works for most projects, but can be customized:

```yaml
# .outputs/exploration/config.yaml

exploration:
  # Delta exploration scope
  include_uncommitted: true
  max_file_size: 1048576  # 1MB limit per file
  ignore_patterns:
    - "node_modules/**"
    - "*.lock"
    - "dist/**"
    - "build/**"

  # Analysis depth
  trace_dependencies: true
  analyze_imports: true
  detect_patterns: true

  # Output format
  include_code_samples: false
  max_sample_lines: 10
```

**Environment Variables:**
```bash
export DEEP_EXPLORER_OUTPUT_DIR=".outputs/exploration/"
export DEEP_EXPLORER_INCLUDE_UNCOMMITTED="true"
```

---

## Notes

- **Git Required:** This skill requires a Git repository for delta tracking
- **Baseline Tracking:** First run establishes baseline, subsequent runs use delta
- **Uncommitted Changes:** Detected and flagged as work in progress
- **No Git Commits:** Does not commit exploration reports to Git
- **Flexible:** Works with dirty working directory
- **Efficient:** Only re-explores changed areas on delta runs
