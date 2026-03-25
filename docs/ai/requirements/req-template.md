# Requirement: {Feature Name}

> Generated: {YYYY-MM-DD}
> Status: Draft | Review | Approved
> Complexity: Low | Medium | High

Note: All content in this document must be written in English.

---

## Quick Links

| Document | Status |
|----------|--------|
| [BA Analysis](agents/ba-{name}.md) | ✅ Complete / ⏭️ Skipped |
| [SA Assessment](agents/sa-{name}.md) | ✅ Complete / ⏭️ Skipped |
| [Domain Research](agents/research-{name}.md) | ✅ Complete / ⏭️ Skipped |
| [UI/UX Design](agents/uiux-{name}.md) | ✅ Complete / ⏭️ Skipped |

---

## 1. Executive Summary

{3-5 sentences covering: what is being built, why it matters, and how it will be approached}

---

## 2. Problem Statement

### Context
{Business/technical context that led to this requirement}

### Problem
{The specific problem to be solved}

### Impact
{Consequences if not addressed - business value, user pain points}

---

## 3. Users & User Stories

### Target Users

| User Type | Description | Primary Goals |
|-----------|-------------|---------------|
| {User 1} | {Who they are} | {What they want to achieve} |

### User Stories

| ID | Priority | As a... | I want to... | So that... |
|----|----------|---------|--------------|------------|
| US-01 | Must | {user} | {action} | {benefit} |
| US-02 | Must | {user} | {action} | {benefit} |
| US-03 | Should | {user} | {action} | {benefit} |

---

## 4. Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-01 | {Description} | Must | {How to verify} |
| FR-02 | {Description} | Must | {How to verify} |
| FR-03 | {Description} | Should | {How to verify} |
| FR-04 | {Description} | Could | {How to verify} |

**Priority Legend:**
- **Must**: Critical for release
- **Should**: Important but not blocking
- **Could**: Nice to have

---

## 5. Business Rules

| ID | Rule | Condition | Action |
|----|------|-----------|--------|
| BR-01 | {Rule Name} | When {condition} | Then {action} |
| BR-02 | {Rule Name} | When {condition} | Then {action} |

---

## 6. Technical Assessment

### Feasibility Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| Overall | ✅ Feasible / ⚠️ Conditional / ❌ Issues | {Summary} |
| Frontend | 🟢 Low / 🟡 Medium / 🔴 High | {Complexity notes} |
| Backend | 🟢 Low / 🟡 Medium / 🔴 High | {Complexity notes} |
| Data | 🟢 Low / 🟡 Medium / 🔴 High | {Complexity notes} |

### Recommended Architecture

{Brief description of recommended approach}

### Technology Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| {Layer} | {Tech} | {Why} |

### Technical Risks

| ID | Risk | Impact | Likelihood | Mitigation |
|----|------|--------|------------|------------|
| TR-01 | {Risk} | High/Med/Low | High/Med/Low | {Mitigation} |

---

## 7. UI/UX Design (if applicable)

### Screen Inventory

| # | Screen | Purpose | Priority |
|---|--------|---------|----------|
| 1 | {Screen name} | {Purpose} | Must |

### Key User Flows

{Flow diagram or description}

### Wireframe Reference

See: [UI/UX Design Document](agents/uiux-{name}.md)

---

## 8. Domain Context (if applicable)

### Glossary

| Term | Definition |
|------|------------|
| {Term} | {Clear definition in project context} |

### Compliance & Standards

| Standard | Applicability |
|----------|---------------|
| {Standard name} | {How it applies} |

---

## 9. Non-Functional Requirements (Optional)

| Category | Requirement |
|----------|-------------|
| **Performance** | {e.g., Response time < 200ms} |
| **Security** | {e.g., Authentication required} |
| **Compatibility** | {e.g., Chrome 90+, mobile responsive} |
| **Accessibility** | {e.g., WCAG 2.1 AA compliance} |

---

## 10. Technical Edge Cases

| ID | Category | Edge Case | Expected Behavior | Priority |
|----|----------|-----------|-------------------|----------|
| TE-01 | {Concurrency/Data/Network/Security/Performance} | {Description} | {How system should handle it} | Must/Should |

---

## 11. Edge Cases & Constraints

### Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| {Edge case description} | {How system should handle it} |

### Constraints

- **Technical**: {e.g., Must use existing auth system}
- **Business**: {e.g., Budget limit, timeline}
- **Dependencies**: {e.g., Requires API v2 ready}

---

## 12. Out of Scope

> Explicitly excluded from this requirement

- {Feature/functionality not included}
- {Deferred to future iteration}

---

## 13. Open Questions

| ID | Question | Owner | Due Date | Status | Blocking |
|----|----------|-------|----------|--------|----------|
| Q-01 | {Unresolved question} | {Who decides} | {YYYY-MM-DD} | Open | Yes/No |

---

## 14. Acceptance Criteria

### Scenario 1: {Happy Path - Main Flow}

- **Given** {initial context/state}
- **When** {action performed}
- **Then** {expected outcome}

### Scenario 2: {Alternative Flow}

- **Given** {context}
- **When** {action}
- **Then** {outcome}

### Scenario 3: {Error Handling}

- **Given** {context}
- **When** {invalid action/error condition}
- **Then** {error handling behavior}

---

## 15. Implementation Guidance

### Suggested Phases

| Phase | Focus | Priority |
|-------|-------|----------|
| 1 | {Foundation} | High |
| 2 | {Core features} | High |
| 3 | {Enhancement} | Medium |

### Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {Dependency} | Internal/External | Available/Pending |

---

## 16. Implementation Readiness Score

**Score**: {0-100}%

| Criteria | Status | Weight |
|----------|--------|--------|
| All FRs have testable acceptance criteria | ✅ / ❌ | 20% |
| No critical open questions | ✅ / ❌ | 20% |
| Technical risks have mitigations | ✅ / ❌ | 15% |
| Business rules are explicit | ✅ / ❌ | 15% |
| Error/edge cases defined | ✅ / ❌ | 15% |
| UI/UX specs complete (if applicable) | ✅ / ❌ / N/A | 15% |

**Missing for 100%**:
- {item 1}
- {item 2}

---

## 17. Changelog

| Date | Change |
|------|--------|
| {YYYY-MM-DD} | Initial version |

---

## 18. References

- **Related Docs**: {links to related requirements, designs}
- **External Links**: {Jira tickets, Figma, API docs}
- **Agent Outputs**: See Quick Links section

---

## Related Plans (Optional)

> Remove this section if no epic or feature plans are linked.

| Type | Document | Status | Scope |
|------|----------|--------|-------|
| Epic | [epic-{name}.md](../planning/epic-{name}.md) | open/in_progress/blocked/completed | {Requirement-wide tracking} |
| Feature Plan | [feature-{name}.md](../planning/feature-{name}.md) | open/in_progress/blocked/completed | {FR-01, FR-02} |

---

## Next Steps

1. [ ] Review this requirement document
2. [ ] Address open questions
3. [ ] Run `/create-plan` to generate implementation plan (small feature)
4. [ ] Run `/manage-epic` to break into feature plans (large feature)
