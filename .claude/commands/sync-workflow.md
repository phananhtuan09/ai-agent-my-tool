---
name: sync-workflow
description: Syncs Claude Code workflows to Cursor, GitHub Copilot, OpenCode, and Factory Droid formats.
---

## Goal

Sync selected Claude Code workflow assets to selected target platforms by:
1. Asking the user which platforms to sync
2. Asking which asset types or specific items to migrate
3. Treating `.claude/` as the migration source of truth
4. Applying `docs/ai/tooling/capability-map.md` when a target tool needs concept translation
5. Syncing only the requested scope to reduce runtime and conversion errors

## Source of Truth

For workflow migration, `.claude/` is the single source of truth.

When content exists in multiple tool folders:
- Read `.claude/` first
- Preserve the Claude structure and wording by default
- Copy content directly when the target tool supports the same concept natively
- Use `docs/ai/tooling/capability-map.md` to add a `Tool Mapping` section when direct copy is not enough

Do not merge behavior from other mirrors unless the user explicitly asks for a reverse sync or comparison.

## Step 1: Select Migration Scope

**Tool:** AskUserQuestion

Ask the user three things before any conversion work:
- Which target platforms to sync
- Which asset types to migrate
- Whether to sync all selected items, only missing/outdated items, or a specific named subset

```
AskUserQuestion(
  questions=[
    {
      "question": "Which platforms do you want to sync to?",
      "header": "Platforms",
      "multiSelect": true,
      "options": [
        {"label": "Cursor", "description": ".cursor/commands/, .cursor/rules/"},
        {"label": "GitHub Copilot", "description": ".github/prompts/, copilot-instructions.md"},
        {"label": "OpenCode", "description": ".opencode/command/, skill/, agent/"},
        {"label": "Factory Droid", "description": ".factory/commands/, skills/, droids/"}
      ]
    },
    {
      "question": "Which workflow assets should be migrated?",
      "header": "Assets",
      "multiSelect": true,
      "options": [
        {"label": "Commands", "description": "Sync `.claude/commands/*.md`"},
        {"label": "Skills", "description": "Sync `.claude/skills/**/SKILL.md`"},
        {"label": "Agents", "description": "Sync `.claude/agents/*.md`"},
        {"label": "Output Styles", "description": "Sync `.claude/output-styles/*.md`"},
        {"label": "Themes", "description": "Sync `.claude/themes/*`"},
        {"label": "Scripts", "description": "Sync reusable `.claude/scripts/*` helpers"},
        {"label": "Base Instructions", "description": "Sync `.claude/CLAUDE.md` and derived `AGENTS.md`"}
      ]
    },
    {
      "question": "How broad should this sync be?",
      "header": "Scope",
      "multiSelect": false,
      "options": [
        {"label": "Missing or outdated", "description": "Fast default: sync only items that need updates"},
        {"label": "Everything selected", "description": "Force-sync every selected item"},
        {"label": "Specific items", "description": "Sync only named commands, skills, agents, or files"}
      ]
    }
  ]
)
```

If the user chooses `Specific items`, ask one short follow-up message in chat for the exact names or paths before continuing.

---

## Step 2: Load Common Analysis and Capability Mapping

**References:**
- Read and follow `docs/sync-workflow/common.md`
- Read and follow `docs/ai/tooling/capability-map.md`

This step:
- Analyzes only the selected `.claude/` source files
- Detects existing target files only for the selected platforms and asset types
- Classifies files as MISSING, OUTDATED, or CURRENT
- Decides when direct copy is safe versus when a `Tool Mapping` section is required

---

## Step 3: Execute Platform-Specific Sync

For each selected platform, load and execute the corresponding guide.

Rules:
- Sync only the asset types selected in Step 1
- If scope is `Missing or outdated`, skip CURRENT items
- If scope is `Specific items`, touch only the explicitly named items
- Preserve `.claude` wording by default and only adapt the parts required by the target tool
- When a target tool lacks a Claude capability, add a `Tool Mapping` section using `docs/ai/tooling/capability-map.md`

### If Cursor selected:
**Reference:** Read and follow `docs/sync-workflow/cursor.md`

### If GitHub Copilot selected:
**Reference:** Read and follow `docs/sync-workflow/github-copilot.md`

### If OpenCode selected:
**Reference:** Read and follow `docs/sync-workflow/opencode.md`

### If Factory Droid selected:
**Reference:** Read and follow `docs/sync-workflow/factory-droid.md`

---

## Step 4: Sync Base Instructions Only When Selected

Only execute this step if `Base Instructions` was selected in Step 1.

Many AI coding tools use `AGENTS.md` as their base instruction file:
- OpenCode, Factory Droid - read natively
- Cursor, GitHub Copilot - support AGENTS.md

### 4a: Read Source

Read `.claude/CLAUDE.md` as the primary source.
Treat it as authoritative for migration unless the user explicitly asks to sync from another base instruction file.

### 4b: Convert Content

**Conversion rules for AGENTS.md:**

1. **Remove Claude-specific syntax:**
   - Remove `AskUserQuestion(...)` tool references
   - Remove `Task(subagent_type=...)` syntax
   - Convert `Read/Write/Edit` tool calls to generic instructions
   - Remove `.claude/skills/...` paths

2. **Keep universal content:**
   - Core coding philosophy
   - Workflow guidelines
   - File structure conventions
   - Communication guidelines
   - Code presentation rules
   - TODO policy
   - Git workflow
   - Quality gates

3. **Use capability mapping:**
   - Follow `docs/ai/tooling/capability-map.md`
   - Convert Claude capabilities into generic behavior statements
   - Add a short `Tool Mapping` section when the target tool needs clarification beyond direct copy

### 4c: Write to AGENTS.md

Write converted content only when the selected target platform uses or benefits from `AGENTS.md`.

---

## Step 5: Summary Report

Generate sync report based on the user's selected scope:

```
## Workflow Sync Complete

### Platforms Synced
- [x] Cursor (if selected)
- [x] GitHub Copilot (if selected)
- [x] OpenCode (if selected)
- [x] Factory Droid (if selected)

### Asset Types Synced
- [x] Commands (if selected)
- [x] Skills (if selected)
- [x] Agents (if selected)
- [x] Output Styles (if selected)
- [x] Themes (if selected)
- [x] Scripts (if selected)
- [x] Base Instructions (if selected)

### Scope
- Mode: [Missing or outdated / Everything selected / Specific items]
- Named items: [list when applicable]

### Files Created/Updated
[List files per platform]

### Warnings
[Any conversion warnings]

### Skipped
- [CURRENT items skipped because scope was `Missing or outdated`]
- [Asset groups not selected]

### Next Steps
- Review converted files
- Test commands in each platform
- Commit changes
```

---

## Notes

### Platform Comparison Summary

| Feature | Claude Code | Cursor | GitHub Copilot | OpenCode | Factory Droid |
|---------|-------------|--------|----------------|----------|---------------|
| Commands | `.claude/commands/` | `.cursor/commands/` | `.github/prompts/` | `.opencode/command/` | `.factory/commands/` |
| Skills | `.claude/skills/*/SKILL.md` | `.cursor/rules/` | N/A | `.opencode/skill/*/SKILL.md` | `.factory/skills/*/SKILL.md` |
| Agents | `.claude/agents/*.md` | N/A | N/A | `.opencode/agent/*.md` | `.factory/droids/*.md` |
| Base | `CLAUDE.md` | `CLAUDE.md` | `copilot-instructions.md` | `AGENTS.md` | `AGENTS.md` |

### When to Run This Command

- After adding/modifying Claude commands or skills
- When only one workflow asset needs to be migrated quickly
- After major updates to platform documentation
- Before releasing new version of ai-workflow-init package
- When team reports sync issues between platforms
