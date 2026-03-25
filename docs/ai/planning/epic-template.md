# Epic: {Epic Name}

Note: All content in this document must be written in English.

---
requirement: {docs/ai/requirements/req-xxx.md or null}
---

## 1. Overview

[1-3 sentences: what this epic delivers and why it needs to be broken into multiple feature plans]

---

## 2. Feature Plans

| # | Feature Plan | Priority | Status | FR Scope | Depends On | Description |
|---|-------------|----------|--------|----------|------------|-------------|
| 1 | [feature-{name}-part1.md](feature-{name}-part1.md) | P{0-4} | open | FR-01, FR-02 | - | {Brief description} |
| 2 | [feature-{name}-part2.md](feature-{name}-part2.md) | P{0-4} | open | FR-03 | feature-{name}-part1 | {Brief description} |

**Status values:** `open` | `in_progress` | `blocked` | `completed`

Use `-` for `FR Scope` or `Depends On` when the workflow does not need that level of tracking.

---

## 3. Dependency Graph

```
Feature 1 ──────────────────┐
                            ▼
Feature 3 ───▶ Feature 2 ───▶ Feature 4
```

---

## 4. Related Documents

- **Requirement**: [req-{name}.md](../requirements/req-{name}.md)

---

## Changelog

| Date | Change |
|------|--------|
| {YYYY-MM-DD} | Epic created |
