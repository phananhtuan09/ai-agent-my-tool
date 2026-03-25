# Epic: AI Agent Tool Delivery

Note: All content in this document must be written in English.

---
requirement: docs/ai/requirements/req-ai-agent-tool.md
---

## 1. Overview

This epic breaks the requirement into one foundation slice plus three agent-specific feature plans. The foundation slice establishes the FastAPI + HTMX shell, agent registry, config hot-swap skeleton, and SSE plumbing so the remaining agent plans can focus on domain behavior instead of bootstrapping.

---

## 2. Feature Plans

| # | Feature Plan | Priority | Status | FR Scope | Depends On | Description |
|---|-------------|----------|--------|----------|------------|-------------|
| 1 | [feature-ai-agent-foundation.md](feature-ai-agent-foundation.md) | P0 | completed | FR-01, FR-02, FR-03, FR-04, FR-05, FR-06 | - | Build the application shell, shared runtime, registry auto-discovery, settings persistence, SSE streaming, and placeholder agent pages. |
| 2 | [feature-job-finder-agent.md](feature-job-finder-agent.md) | P1 | completed | FR-07, FR-08, FR-09, FR-10, FR-11, FR-12, FR-13, FR-14 | feature-ai-agent-foundation | Implement job crawling, hard filtering, AI ranking, retention, and failure reporting on top of the shared shell. |
| 3 | [feature-daily-schedule-agent.md](feature-daily-schedule-agent.md) | P1 | completed | FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21 | feature-ai-agent-foundation | Implement task parsing, timeline rendering, reminder cron jobs, and interactive rescheduling for the daily schedule workflow. |
| 4 | [feature-crypto-airdrop-agent.md](feature-crypto-airdrop-agent.md) | P2 | completed | FR-22, FR-23, FR-24, FR-25, FR-26, FR-27 | feature-ai-agent-foundation | Implement the airdrop crawler, scoring flow, retention rules, and chat filtering with the initial source list of airdrops.io, CryptoRank, and DeFiLlama. |

**Status values:** `open` | `in_progress` | `blocked` | `completed`

---

## 3. Dependency Graph

```text
feature-ai-agent-foundation
        ├──────────────▶ feature-job-finder-agent
        ├──────────────▶ feature-daily-schedule-agent
        └──────────────▶ feature-crypto-airdrop-agent
```

---

## 4. Related Documents

- **Requirement**: [req-ai-agent-tool.md](../requirements/req-ai-agent-tool.md)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-24 | Epic created from the requirement document and decomposed into one foundation slice plus three agent-specific feature plans |
| 2026-03-24 | Foundation slice moved to `in_progress` after the first implementation pass and environment-limited verification |
| 2026-03-24 | Job Finder plan created, reviewed, and moved to `in_progress` after the first implementation pass |
| 2026-03-24 | Daily Schedule plan created and moved to `in_progress` after the first implementation pass with environment-limited verification |
| 2026-03-24 | Crypto Airdrop plan created and moved to `in_progress` after the first implementation pass with the confirmed initial source list |
| 2026-03-25 | Full implementation re-verified with dependency-backed local validation, persistence isolation fixes, and feature statuses moved to `completed` |
