---
name: manage-epic
description: Create or update epic - tracks feature plans for a requirement.
---

## Goal

Manage epic documents that link requirements to feature plans. An epic is a simple tracking document that lists all feature plans needed to fulfill a requirement.

**When to use:**
- A requirement is too large for a single feature plan
- You need to break a requirement into multiple feature plans
- You need to update an epic with new feature plans or status changes

---

## Workflow Alignment

- Provide brief status updates (1–3 sentences) before/after important actions.
- For medium/large tasks, create todos (≤14 words, verb-led). Keep only one `in_progress` item.
- Update todos immediately after progress; mark completed upon finish.

---

## Step 1: Detect Mode

**Parse user input to determine mode:**

| Input | Mode | Action |
|-------|------|--------|
| Requirement doc path provided | **Create** | Create new epic from requirement |
| Epic doc path provided | **Update** | Update existing epic |
| Feature plan path + epic path | **Link** | Add feature plan to epic |
| No specific path | **Ask** | Ask user what they want to do |

**If unclear, ask:**

```
AskUserQuestion(questions=[{
  question: "What would you like to do with the epic?",
  header: "Mode",
  options: [
    { label: "Create new epic", description: "Break a requirement into feature plans" },
    { label: "Update epic", description: "Add feature plan or update status" },
    { label: "Sync status", description: "Update status of all linked documents" }
  ],
  multiSelect: false
}])
```

---

## Step 2: Create Mode

### 2a: Read Requirement

```
Read(file_path="docs/ai/requirements/req-{name}.md")
```

Extract:
- Feature name
- Functional requirements (FR table)
- Implementation guidance / suggested phases
- Complexity level

### 2b: Break into Feature Plans

Analyze the requirement and propose how to break it into feature plans.

**Guidelines:**
- Each feature plan should be independently implementable
- Group by: feature area, layer (frontend/backend), or dependency order
- Aim for 2-6 feature plans per epic
- Each plan should map to specific FRs from the requirement

**Ask user to confirm breakdown:**

```
AskUserQuestion(questions=[{
  question: "Here's the proposed breakdown. Does this look right?",
  header: "Breakdown",
  options: [
    { label: "Looks good", description: "Create epic with this breakdown" },
    { label: "Adjust", description: "I want to modify the breakdown" },
    { label: "Fewer plans", description: "Merge some plans together" }
  ],
  multiSelect: false
}])
```

### 2c: Load Template & Generate Epic

```
Read(file_path="docs/ai/planning/epic-template.md")
```

Generate `docs/ai/planning/epic-{name}.md` with:
- `requirement` frontmatter pointing to the req doc
- Overview: 1-3 sentences from requirement's executive summary
- Feature Plans table: proposed feature plans with descriptions, plus `FR Scope` and `Depends On` when the epic template tracks them
- Dependency graph: show dependencies between feature plans
- Related Documents: link back to requirement

**Auto-name:** Derive from requirement name (kebab-case).
- Example: `req-user-authentication.md` → `epic-user-authentication.md`

**If file already exists:**
1. Backup to `docs/ai/planning/archive/epic-{name}_{timestamp}.md`
2. Overwrite main file
3. Notify user of backup

### 2d: Update Requirement Doc

After creating epic, update the requirement doc's frontmatter and Related Plans section:
- Set `epic_plan` in frontmatter
- Update Related Plans table with epic link

---

## Step 3: Update Mode

### 3a: Read Current Epic

```
Read(file_path="docs/ai/planning/epic-{name}.md")
```

### 3b: Determine Update Type

| Trigger | Action |
|---------|--------|
| New feature plan created | Add row to Feature Plans table |
| Feature plan completed | Update status to `completed` |
| Feature plan started | Update status to `in_progress` |
| Feature plan blocked | Update status to `blocked` |
| Dependency changed | Update dependency graph |

### 3c: Apply Update

Edit the epic document with the change. Keep all other content intact.

If the epic table contains `FR Scope` or `Depends On` columns:
- update those values when the new information is available

If the epic table uses the older shape without those columns:
- preserve the current table shape
- encode dependency detail in the dependency graph or description instead

---

## Step 4: Link Mode

When a new feature plan is created (e.g., via `/create-plan`), link it to the epic:

1. Read the epic document
2. Add the feature plan to the Feature Plans table
3. Update the feature plan's `epic_plan` frontmatter to point to the epic
4. Populate `FR Scope` and `Depends On` when the epic table tracks them
5. Update dependency graph if needed

---

## Step 5: Sync Status

Scan all linked documents and synchronize status:

1. Read the epic document
2. For each feature plan in the table:
   - Read the feature plan
   - Check if implementation tasks are completed
   - Detect explicit blockers
   - Update status in epic table
3. Update requirement doc if all feature plans are completed

**Default status mapping:**
- No completed implementation tasks yet → `open`
- Some completed tasks and some remaining → `in_progress`
- Explicit blocker recorded in the feature plan → `blocked`
- All implementation tasks complete → `completed`

---

## Step 6: Summary & Next Steps

```markdown
## Epic Updated

**File**: docs/ai/planning/epic-{name}.md

### Feature Plans
| # | Plan | Status |
|---|------|--------|
| 1 | feature-{name}-part1.md | {status} |
| 2 | feature-{name}-part2.md | {status} |

### Next Steps
- `/create-plan` → Create a feature plan listed in this epic
- `/execute-plan` → Implement a feature plan
- `/manage-epic` → Update status or add feature plans
```

---

## Cross-Linking Rules

When creating or updating documents, ensure cross-links are maintained.
**Only add links when they exist — never add placeholder/null links.**

### Creating Epic from Requirement (`/manage-epic`)
1. Epic: set `requirement` frontmatter → req doc path
2. Req doc: add or update the "Related Plans" section with epic link

### Adding Feature Plan to Epic (`/create-plan` with epic context)
1. Epic: add row to Feature Plans table
2. Feature plan: set `epic_plan` frontmatter → epic path
3. Feature plan: set `requirement` frontmatter → req doc path (from epic)
4. Feature plan: include Section 0 "Related Documents" with both links

### Creating Feature Plan standalone (`/create-plan` without epic or req)
1. Feature plan: frontmatter `epic_plan` = null, `requirement` = null
2. Feature plan: **remove** Section 0 "Related Documents" entirely
3. No cross-linking needed

---

## Error Handling

| Error | Action |
|-------|--------|
| Requirement doc not found | Ask user for path or create requirement first |
| Epic already exists | Ask: update existing or create new (backup old) |
| Feature plan not found | Skip link, warn user |
| Template not found | Use minimal structure from this command |

---

## Notes

- Epic is purely a tracking document — no architecture or implementation details
- Feature plans contain all implementation details (via `/create-plan`)
- Requirement doc contains all WHAT details (via `/requirements-orchestrator`)
- Epic bridges the gap: tracks WHICH feature plans implement WHICH requirement
- Status values supported by the epic template: `open`, `in_progress`, `blocked`, `completed`
