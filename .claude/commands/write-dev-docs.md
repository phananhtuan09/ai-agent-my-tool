---
name: write-dev-docs
description: Generates technical documentation about programming techniques in docs/dev folder.
---

Generate comprehensive documentation about programming techniques.

## Workflow Alignment

- Provide brief status updates (1-3 sentences) before/after important actions.
- For medium/large tasks, create todos (<=14 words, verb-led). Keep only one `in_progress` item.
- Update todos immediately after progress; mark completed upon finish.

## Step 1: Gather Input (Context-Aware)

**Auto-detect context from 2 sources:**

1. **From command arguments** (user provides topic directly):
   - `/write-dev-docs memoization` → Topic: memoization
   - `/write-dev-docs dependency injection in TypeScript` → Topic: dependency injection, Context: TypeScript

2. **From conversation history** (user references current discussion):
   - Keywords: "note this", "save this", "from discussion", "this technique", "above technique", "current topic"
   - Example: `/write-dev-docs note this technique` → Extract technique from conversation above
   - Scan conversation for: technique name, code examples, language/framework discussed

**Decision flow:**
```
IF command has specific topic (e.g., "memoization", "factory pattern")
  → Use that topic directly
ELSE IF command references conversation ("note this", "this technique", etc.)
  → Extract topic from conversation history
ELSE (no context available)
  → Use AskUserQuestion to ask user
```

**Only use AskUserQuestion when NO context found:**

If topic is unclear:
```
Question: "What programming technique do you want to document?"
Header: "Topic"
Options:
  - "Design Pattern" - Architecture and design patterns (singleton, factory, observer, etc.)
  - "Performance" - Optimization techniques (memoization, caching, lazy loading)
  - "Testing" - Testing strategies and methodologies
```

If language/framework context is needed and not clear:
```
Question: "What context for this technique?"
Header: "Context"
Options:
  - "General" - Language-agnostic concepts
  - "JavaScript/TypeScript" - JS/TS specific implementation
  - "Python" - Python specific implementation
```

## Step 2: Research & Structure

**Research the technique:**
- Core concepts and principles
- Common use cases and applications
- Best practices and pitfalls to avoid
- Real-world examples

**Document structure:**
```markdown
# [Technique Name]

## Overview
Brief introduction and why this technique matters.

## Core Concepts
Key principles and fundamentals.

## When to Use
- Use cases where this technique shines
- Scenarios to avoid

## Implementation

### Basic Example
```[language]
// Simple example with comments
```

### Advanced Example
```[language]
// More complex real-world example
```

## Best Practices
- Do's and don'ts
- Common mistakes to avoid

## Trade-offs
| Pros | Cons |
|------|------|
| ... | ... |

## Related Techniques
Links to related concepts/patterns.

## References
- Official docs, articles, books
```

## Step 3: Generate Documentation

**Output file:** `docs/dev/{technique-name}.md`

**Naming convention:**
- Use kebab-case for file names
- Example: `dependency-injection.md`, `memoization.md`, `event-sourcing.md`

**Content guidelines:**
- **Write all content in English** (titles, explanations, code comments)
- Include practical code examples
- Focus on "why" and "when" not just "how"
- Keep explanations clear and concise
- Add inline comments in code examples (in English)

## Step 4: Review & Finalize

- Ensure all sections are complete
- Verify code examples are syntactically correct
- Check for clarity and readability
- Confirm file is saved in `docs/dev/`

## Notes

- **Creates:** Documentation files in `docs/dev/` only
- **Focus on:** Practical, actionable knowledge
- **Avoid:** Overly academic or theoretical content without examples
- Idempotent: safe to re-run; updates doc if already exists

**Example topics:**
- Design patterns (singleton, factory, observer, etc.)
- Programming paradigms (functional, OOP, reactive)
- Performance techniques (memoization, lazy loading, caching)
- Architecture patterns (MVC, CQRS, event sourcing)
- Testing strategies (TDD, BDD, property-based testing)
- Concurrency patterns (async/await, actors, CSP)
