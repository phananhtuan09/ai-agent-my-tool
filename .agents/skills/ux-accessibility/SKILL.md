---
name: ux-accessibility
description: Use when the task involves accessible UI behavior such as keyboard navigation, focus management, screen reader support, semantic HTML, ARIA, or contrast-sensitive design.
---

# UX Accessibility

## Purpose
Ensure UI is usable and accessible for everyone, including people with disabilities. Accessible design benefits all users.

---

## Core Principle

**Accessible design is good design for everyone.**

Benefits:
- Improves UX for all users
- Better SEO (semantic HTML)
- Legal compliance (ADA, WCAG)
- Broader audience reach

---

## Keyboard Navigation

### All Interactive Elements Must Be Keyboard-Accessible

**Required keyboard controls:**
- **Tab**: Move forward through interactive elements
- **Shift + Tab**: Move backward
- **Enter/Space**: Activate buttons and links
- **Escape**: Close modals, dismiss dropdowns
- **Arrow keys**: Navigate lists, menus, tabs

### Semantic HTML First

**Use native HTML elements—they have built-in keyboard support:**
- Use `<button>` for actions (not `<div>` with click handler)
- Use `<a>` for navigation
- Use `<input>`, `<select>`, `<textarea>` for form controls
- Native elements work automatically with keyboards and screen readers

### Tab Order

**Principle:** Logical tab order matches visual order.

**Guidelines:**
- Default DOM order usually correct
- Avoid positive `tabindex` values (breaks natural order)
- Use `tabindex="0"` to make non-interactive elements focusable
- Use `tabindex="-1"` to remove from tab order but keep programmatically focusable

### Skip Links

**Let keyboard users skip repetitive navigation:**
- Link at top of page: "Skip to main content"
- Visually hidden by default
- Visible on keyboard focus
- Jumps to main content area

---

## Focus Management

### Visible Focus Indicators

**Users must always see which element has focus.**

**Guidelines:**
- Never remove focus outline completely
- If hiding default outline, provide clear alternative
- Minimum 2px outline with sufficient contrast
- Use offset to separate from element border
- `:focus-visible` to show focus only for keyboard (not mouse clicks)

**Contrast requirement:** Focus indicator: 3:1 contrast ratio minimum

### Focus Trapping (Modals)

**Focus stays within modal until dismissed.**

**Requirements:**
1. Move focus to modal when opened
2. Trap focus inside modal (can't tab out)
3. Return focus to trigger element when closed
4. Escape key closes modal

### Focus on Route Changes

**Announce page changes to screen readers:**
- Move focus to page heading on route change
- Or announce change via ARIA live region
- Prevents keyboard users from losing context

---

## Screen Reader Support

### Semantic HTML

**Use correct HTML elements for their purpose:**
- Buttons: `<button>` for actions
- Links: `<a>` for navigation
- Headings: `<h1>`-`<h6>` in proper hierarchy (don't skip levels)
- Lists: `<ul>`, `<ol>`, `<li>` for related items
- Landmarks: `<nav>`, `<main>`, `<header>`, `<footer>`, `<aside>`
- Forms: `<label>`, `<input>`, `<fieldset>`, `<legend>`

### Heading Hierarchy

**Rules:**
- One `<h1>` per page (page title)
- Don't skip heading levels (h1 → h2 → h3, not h1 → h3)
- Headings describe content that follows
- Visual size doesn't matter (use CSS), semantic level does

### ARIA Attributes

**ARIA fills gaps where HTML semantics insufficient.**

**ARIA rules:**
1. First rule: Don't use ARIA (use semantic HTML instead)
2. Don't override native semantics
3. All interactive ARIA controls must be keyboard accessible
4. Don't use `role="presentation"` or `aria-hidden="true"` on focusable elements

**Common ARIA attributes:**
- `aria-label`: Accessible name for element
- `aria-labelledby`: Points to element(s) that label this element
- `aria-describedby`: Points to element(s) that describe this element
- `aria-hidden`: Hides element from screen readers
- `aria-live`: Announces dynamic content changes
- `aria-expanded`: Indicates if element is expanded/collapsed
- `aria-required`: Marks form field as required
- `aria-invalid`: Marks form field as invalid

### Live Regions

**Announce dynamic content changes to screen readers.**

**Politeness levels:**
- `aria-live="polite"`: Announce when user idle (status updates)
- `aria-live="assertive"`: Announce immediately (errors, urgent alerts)
- `aria-live="off"`: Don't announce (default)

**Use cases:** Form validation errors, success messages, loading states, item counts

### Alternative Text

**Images:**
- Informative images: Descriptive alt text
- Decorative images: Empty alt (`alt=""`) or `aria-hidden="true"`

**Icons:**
- Icon with visible text: Hide icon from screen readers
- Icon-only button: Provide accessible label

---

## Color and Contrast

### Contrast Ratios (WCAG AA)

**Minimum ratios:**
- Normal text (<18px): **4.5:1**
- Large text (18px+ or 14px+ bold): **3:1**
- UI components (buttons, borders): **3:1**
- Focus indicators: **3:1**

**Testing:** Use browser DevTools, WebAIM Contrast Checker, or Lighthouse

### Don't Rely on Color Alone

**Information must be conveyed through multiple means:**
- Error fields: Red color + error icon + error text
- Required fields: Asterisk + label text + `required` attribute
- Links in text: Color + underline
- Status indicators: Color + icon + text label

---

## Forms Accessibility

### Labels Required

**Every input needs an accessible label:**
- Visible `<label>` element (preferred)
- `aria-label` for compact UIs
- `aria-labelledby` pointing to existing text

**Don't use placeholder as label** (disappears when typing, insufficient contrast)

### Required Fields

**Indicate required fields:**
- Visual indicator (asterisk)
- Text in label ("Email (required)")
- `required` attribute
- `aria-required="true"`

### Error Messages

**Errors must be associated with fields:**
- Show error inline (near field)
- Use `aria-describedby` to associate error with field
- Use `aria-invalid="true"` to mark field as invalid
- Include error icon for visibility
- Use `role="alert"` for dynamic errors

**Error message content:** Specific, explain what's wrong, suggest how to fix

### Fieldsets and Legends

**Group related form fields:**
- Use for radio button groups, checkbox groups, address forms
- `<fieldset>` wraps group
- `<legend>` provides group label

---

## Interactive Elements

### Buttons vs Links

**Use correct element for the action:**

**Buttons:**
- Trigger actions (submit, open modal, toggle)
- Stay on same page
- Use `<button>` element

**Links:**
- Navigate to another page/location
- Have meaningful `href`
- Use `<a>` element

### Touch Targets

**Minimum size for tappable elements:**
- Minimum: 44x44px (Apple/Google guidelines)
- Spacing between targets: 8px minimum
- Applies to mobile and desktop (helps motor impairments)

### Disabled States

**Explain why elements are disabled:**
- Provide tooltip or visible text explaining why disabled
- Don't disable if user needs to read content
- Consider "enabled but validation error" instead
- Disabled elements not focusable (may hide from keyboard users)

---

## Modals and Dialogs

### Modal Requirements

**Accessibility checklist:**
- Focus moves to modal when opened
- Focus trapped inside modal
- Escape key closes modal
- Focus returns to trigger on close
- Background content inert (not accessible)
- `role="dialog"` and `aria-modal="true"`
- Modal labeled with `aria-labelledby` or `aria-label`

---

## Navigation and Landmarks

### Landmark Regions

**Semantic sections help navigation:**
- `<header>`: Site/page header
- `<nav>`: Navigation menus
- `<main>`: Primary content (one per page)
- `<aside>`: Complementary content
- `<footer>`: Site/page footer
- `<section>`: Thematic content grouping
- `<article>`: Self-contained content

**Multiple landmarks of same type:** Provide unique labels with `aria-label`

---

## Common Mistakes

1. **No keyboard access** - Interactive elements only work with mouse
2. **Missing focus indicators** - Users can't see where they are
3. **Missing alt text** - Images/icons without alternatives
4. **Poor contrast** - Text hard to read
5. **No labels** - Form inputs without associated labels
6. **Color-only information** - Relying solely on color
7. **Keyboard traps** - Can tab in but not out
8. **Inaccessible modals** - Focus not managed properly
9. **Skipped heading levels** - h1 → h3 (skipping h2)
10. **ARIA overuse** - Using ARIA when semantic HTML would work

---

## Key Takeaway

**Accessibility is not optional—it's fundamental.**

Build with accessibility from the start, not as an afterthought. It's easier, cheaper, and results in better UX for everyone.

Test early and often. Automated tools catch ~30-40% of issues—manual testing is essential.
