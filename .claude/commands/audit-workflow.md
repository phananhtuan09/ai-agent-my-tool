---
name: audit-workflow
description: Audit Claude Code workflow configuration (agents, skills, commands, hooks, output-styles) and provide improvement recommendations.
---

# Workflow Audit

Analyze the Claude Code workflow configuration in this project and provide actionable recommendations.

## Audit Process

### Step 1: Gather Workflow Files

Collect all workflow configuration files:

```
Read and analyze:
- .claude/CLAUDE.md (main instructions)
- .claude/settings.json (hooks configuration)
- .claude/settings.local.json (local hooks)
- .claude/agents/*.md (all agent definitions)
- .claude/skills/*/SKILL.md (all skill definitions)
- .claude/commands/*.md (all command definitions)
- .claude/output-styles/*.md (all output styles)
```

Use Glob to find all files, then Read each one.

### Step 2: Analyze Each Category

For each category, evaluate:

#### 2.1 Skills Analysis

| Criteria | Check |
|----------|-------|
| **Trigger clarity** | Is `description` specific about when to load? |
| **Overlap detection** | Do multiple skills cover same triggers? |
| **Size efficiency** | Is SKILL.md < 500 lines? Uses references for large content? |
| **Progressive disclosure** | Does it use references/ for optional content? |
| **Auto-load frequency** | Does "ALWAYS load when..." appear too often? |

**Overlap detection keywords to check:**
- UI/frontend: `frontend-design-*`, `ux-*`
- Code quality: `quality-*`, `*-review`
- Testing: `*-test`, `writing-test`

#### 2.2 Commands Analysis

| Criteria | Check |
|----------|-------|
| **Purpose clarity** | Is the command's purpose clear from name + description? |
| **Workflow alignment** | Does it follow CLAUDE.md guidelines? |
| **Agent delegation** | Does it use Task tool for complex sub-tasks? |
| **Duplication** | Are there commands that do similar things? |

#### 2.3 Agents Analysis

| Criteria | Check |
|----------|-------|
| **Role clarity** | Is the agent's specialized role well-defined? |
| **Tool access** | Does it have appropriate tool restrictions? |
| **Prompt quality** | Is the prompt concise but complete? |

#### 2.4 Hooks Analysis

| Criteria | Check |
|----------|-------|
| **Necessity** | Is each hook actually needed? |
| **Performance** | Are hooks lightweight (< 1 second execution)? |
| **Error handling** | Do hooks exit gracefully on failure? |
| **Matcher specificity** | Are matchers precise enough? |

#### 2.5 Output Styles Analysis

| Criteria | Check |
|----------|-------|
| **Use case clarity** | When should this style be applied? |
| **Conflict potential** | Does it conflict with other styles? |

#### 2.6 CLAUDE.md Analysis

| Criteria | Check |
|----------|-------|
| **Conciseness** | Is it under 500 lines? No redundant info? |
| **Actionability** | Are instructions clear and actionable? |
| **Conflicts** | Does it conflict with skill instructions? |

### Step 3: Context Usage Estimation

Estimate token usage for each component:

```
Token estimation formula:
- ~4 characters = 1 token (rough estimate)
- Metadata always loaded: name + description (~100-200 tokens each)
- Body loaded on trigger: full content
```

Calculate:
1. **Always-loaded tokens**: Sum of all metadata
2. **Frequently-loaded tokens**: Skills with "ALWAYS load" triggers
3. **On-demand tokens**: Skills with specific triggers

### Step 4: Generate Report

Output format:

```markdown
# Workflow Audit Report

## Summary

| Category | Count | Issues | Recommendations |
|----------|-------|--------|-----------------|
| Skills | X | Y | Z |
| Commands | X | Y | Z |
| Agents | X | Y | Z |
| Hooks | X | Y | Z |
| Output Styles | X | Y | Z |

## Context Budget Analysis

### Always-Loaded (~X tokens)
- CLAUDE.md: ~X tokens
- Skill metadata: ~X tokens (Y skills × ~100 tokens)
- Total baseline: ~X tokens

### Frequently-Loaded (~X tokens per session)
- skill-name-1 (ALWAYS load for frontend): ~X tokens
- skill-name-2 (ALWAYS load for React): ~X tokens

### On-Demand
- skill-name-3: ~X tokens (loads for specific trigger)

## Detailed Findings

### 🔴 Critical Issues
Issues that significantly impact performance or cause errors.

### 🟡 Improvements
Optimizations that would improve efficiency.

### 🟢 Best Practices Followed
Positive patterns worth maintaining.

## Recommendations

### High Priority
1. [Specific actionable recommendation]
   - **Impact**: [What improves]
   - **Effort**: [Low/Medium/High]

### Medium Priority
...

### Low Priority (Nice to Have)
...

## Overlap Analysis

### Potential Skill Overlaps
| Skills | Overlap Area | Recommendation |
|--------|--------------|----------------|
| A, B | frontend triggers | Consider merging or clarifying triggers |

### Command Redundancies
...

## Suggested Consolidations

If skills/commands can be merged:
- Merge `skill-a` + `skill-b` → `combined-skill` (saves ~X tokens)
```

## Analysis Guidelines

### What Makes a Good Workflow

1. **Minimal always-loaded content**: Only essential instructions in CLAUDE.md
2. **Specific triggers**: Skills load only when truly needed
3. **No overlaps**: Each skill/command has unique purpose
4. **Progressive disclosure**: Large content split into references
5. **Lightweight hooks**: Fast execution, graceful failures

### Red Flags to Watch For

- Skills with "ALWAYS load" for broad triggers (e.g., "any code")
- Multiple skills triggering on same keywords
- Commands that duplicate skill functionality
- Hooks that run on every tool use
- CLAUDE.md > 300 lines
- Skills > 500 lines without using references/

### Token Budget Guidelines

| Budget Level | Always-Loaded | Recommendation |
|--------------|---------------|----------------|
| Lean | < 2000 tokens | Excellent |
| Normal | 2000-5000 | Good |
| Heavy | 5000-10000 | Consider optimization |
| Bloated | > 10000 | Needs consolidation |

## Execution

1. Run full analysis
2. Generate report with findings
3. Prioritize recommendations by impact/effort ratio
4. Offer to implement quick wins if user approves
