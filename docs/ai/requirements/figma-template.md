---
frame_url: null
frame_name: null
file_name: null
extracted: null
status: partial  # partial | complete
---

# Figma: {Frame Name}

> **Purpose**: This document captures the complete design specification extracted from Figma.
> It serves two purposes:
> 1. **Implementation guide** — AI agents use this to implement pixel-perfect UI.
> 2. **Validation reference** — used by `/check-implementation` to verify code matches design.

---

## Reference

| Field        | Value             |
|--------------|-------------------|
| File         | {figma-file-name} |
| Frame        | {frame-path}      |
| URL          | {url}             |
| Extracted    | {YYYY-MM-DD}      |
| Status       | partial / complete |

---

## Frame Overview

> High-level description: what is this screen/frame? Who uses it? What is its purpose in the product flow?

**Screen**: {e.g. "Login Page"}
**User type**: {e.g. "Unauthenticated users"}
**Purpose**: {e.g. "Entry point for authentication. User enters credentials and accesses the app."}
**Product flow position**: {e.g. "Landing → Login → Dashboard"}

---

## Layout Structure

> Hierarchical tree of the frame. Shows regions, sections, and groups — not individual leaf nodes.
> Each node includes: name, type (Frame/Group/Component/Text/Icon), purpose.

```
{Frame: Login Page}
├── {Header} [Frame] — Top navigation bar
│   ├── {Logo} [Component] — Brand logo, links to home
│   └── {Nav Links} [Group] — Navigation items
├── {Main Content} [Frame] — Primary content area
│   ├── {Hero} [Group] — Above-the-fold section
│   │   ├── {Headline} [Text] — Primary heading
│   │   ├── {Subheadline} [Text] — Supporting text
│   │   └── {CTA Button} [Component] — Primary action
│   └── {Form} [Group] — Login form area
│       ├── {Email Field} [Component]
│       ├── {Password Field} [Component]
│       └── {Submit Button} [Component]
└── {Footer} [Frame] — Footer with links
```

**Layout type**: {e.g. Single column / Two column / Grid}
**Container max-width**: {e.g. 1280px}
**Main axis**: {e.g. Vertical stack / Horizontal flex}

---

## Design Tokens

### Colors

| Token Name       | Hex Value | Usage                          |
|------------------|-----------|--------------------------------|
| Primary-500      | #3b82f6   | Buttons, links, primary actions |
| Primary-600      | #2563eb   | Button hover state             |
| Primary-700      | #1d4ed8   | Button active/pressed state    |
| Neutral-50       | #f9fafb   | Page background                |
| Neutral-100      | #f3f4f6   | Card background, input fill    |
| Neutral-200      | #e5e7eb   | Borders, dividers              |
| Neutral-400      | #9ca3af   | Placeholder text, disabled     |
| Neutral-600      | #4b5563   | Secondary text                 |
| Neutral-700      | #374151   | Body text                      |
| Neutral-900      | #111827   | Heading text                   |
| Error-500        | #ef4444   | Error messages, destructive    |
| Success-500      | #22c55e   | Success states, confirmations  |
| Warning-500      | #f59e0b   | Warnings, caution states       |

### Typography

| Style Name  | Font Family | Size | Weight | Line Height | Letter Spacing | Usage         |
|-------------|-------------|------|--------|-------------|----------------|---------------|
| Heading-1   | Inter       | 32px | 700    | 40px        | -0.02em        | Page title    |
| Heading-2   | Inter       | 24px | 600    | 32px        | -0.01em        | Section title |
| Heading-3   | Inter       | 20px | 600    | 28px        | 0              | Card title    |
| Body-Large  | Inter       | 18px | 400    | 28px        | 0              | Lead text     |
| Body        | Inter       | 16px | 400    | 24px        | 0              | Body text     |
| Body-Small  | Inter       | 14px | 400    | 20px        | 0              | Secondary text|
| Caption     | Inter       | 12px | 400    | 16px        | 0.01em         | Labels, hints |
| Label       | Inter       | 14px | 500    | 20px        | 0.01em         | Form labels   |
| Button      | Inter       | 16px | 600    | 24px        | 0.01em         | Button text   |
| Code        | JetBrains Mono | 14px | 400 | 20px       | 0              | Code snippets |

### Spacing Scale

| Token    | Value | Usage                              |
|----------|-------|------------------------------------|
| space-1  | 4px   | Micro gaps (icon-to-text)          |
| space-2  | 8px   | Tight spacing (badge padding)      |
| space-3  | 12px  | Input padding vertical             |
| space-4  | 16px  | Default padding, small gaps        |
| space-5  | 20px  | Medium gaps                        |
| space-6  | 24px  | Section internal padding           |
| space-8  | 32px  | Large gaps between elements        |
| space-10 | 40px  | Section dividers                   |
| space-12 | 48px  | Section top/bottom padding         |
| space-16 | 64px  | Major section separation           |
| space-20 | 80px  | Hero section padding               |

### Shadows

| Token       | CSS Value                                   | Usage              |
|-------------|---------------------------------------------|--------------------|
| shadow-sm   | 0 1px 2px rgba(0,0,0,0.05)                  | Cards at rest      |
| shadow-md   | 0 4px 6px -1px rgba(0,0,0,0.1)             | Hovered cards      |
| shadow-lg   | 0 10px 15px -3px rgba(0,0,0,0.1)           | Dropdowns, modals  |
| shadow-xl   | 0 20px 25px -5px rgba(0,0,0,0.1)           | Dialogs, overlays  |

### Border Radius

| Token      | Value | Usage                          |
|------------|-------|--------------------------------|
| radius-sm  | 4px   | Badges, tags                   |
| radius-md  | 8px   | Buttons, inputs                |
| radius-lg  | 12px  | Cards                          |
| radius-xl  | 16px  | Modals, panels                 |
| radius-2xl | 24px  | Large cards, hero sections     |
| radius-full| 9999px| Pills, avatars, toggles        |

---

## Component Specifications

> Each component is documented with all states and variants.
> Format: component-name (figma-id if available)

---

### {Component: Button}

**Figma ID**: {abc123}
**Description**: Primary interactive element for actions.
**States**: default, hover, active, focus, disabled, loading
**Variants**: primary, secondary, outline, ghost, danger

---

#### Variant: Primary

| State    | Background | Text        | Border | Shadow    | Cursor      |
|----------|------------|-------------|--------|-----------|-------------|
| Default  | #3b82f6    | #ffffff     | none   | shadow-sm | pointer     |
| Hover    | #2563eb    | #ffffff     | none   | shadow-md | pointer     |
| Active   | #1d4ed8    | #ffffff     | none   | none      | pointer     |
| Focus    | #3b82f6    | #ffffff     | 2px #93c5fd offset 2px | shadow-sm | pointer |
| Disabled | #e5e7eb    | #9ca3af     | none   | none      | not-allowed |
| Loading  | #3b82f6    | transparent | none   | shadow-sm | wait        |

**Dimensions**:
- Height: 44px (min touch target)
- Min-width: 120px
- Padding: 12px top/bottom, 24px left/right

**Typography**: Button style (Inter 16px 600)
**Border radius**: radius-md (8px)
**Icon**: 20px, 8px gap from text (left or right)
**Loading spinner**: 20px, centered, white

---

#### Variant: Secondary

| State    | Background | Text     | Border                  | Shadow    |
|----------|------------|----------|-------------------------|-----------|
| Default  | #f3f4f6    | #374151  | none                    | none      |
| Hover    | #e5e7eb    | #111827  | none                    | none      |
| Disabled | #f9fafb    | #d1d5db  | none                    | none      |

---

#### Variant: Outline

| State    | Background  | Text     | Border              | Shadow    |
|----------|-------------|----------|---------------------|-----------|
| Default  | transparent | #3b82f6  | 1.5px solid #3b82f6 | none      |
| Hover    | #eff6ff     | #2563eb  | 1.5px solid #2563eb | none      |
| Disabled | transparent | #9ca3af  | 1.5px solid #e5e7eb | none      |

---

#### Size Variants

| Size   | Height | Padding H | Padding V | Font  |
|--------|--------|-----------|-----------|-------|
| small  | 36px   | 16px      | 8px       | 14px  |
| medium | 44px   | 24px      | 12px      | 16px  |
| large  | 52px   | 32px      | 14px      | 18px  |

---

### {Component: Input Field}

**Description**: Text input for forms.
**States**: empty, filled, focused, error, disabled, readonly
**Variants**: text, email, password, search, textarea

---

| State    | Background | Border                    | Text     | Label    |
|----------|------------|---------------------------|----------|----------|
| Empty    | #ffffff    | 1px solid #d1d5db         | -        | #6b7280  |
| Filled   | #ffffff    | 1px solid #d1d5db         | #111827  | #374151  |
| Focused  | #ffffff    | 2px solid #3b82f6         | #111827  | #3b82f6  |
| Error    | #fff5f5    | 2px solid #ef4444         | #111827  | #ef4444  |
| Disabled | #f9fafb    | 1px solid #e5e7eb (dashed)| #9ca3af  | #9ca3af  |

**Dimensions**:
- Height: 44px (single-line), auto (textarea, min 96px)
- Width: 100% of container
- Padding: 12px vertical, 16px horizontal

**Typography**: Body (Inter 16px 400)
**Border radius**: radius-md (8px)
**Label**: Caption style (12px 500), 4px above input
**Helper text**: Caption style (12px 400), 4px below input, Neutral-500
**Error text**: Caption style (12px 400), 4px below input, Error-500
**Icon**: 20px, positioned 12px from edge, Neutral-400 (or Primary-500 when active)

---

### {Add more components here}

> Use the same format: states table + dimensions + typography + notes

---

## Responsive Specifications

### Breakpoints

| Name    | Range        | Container Width |
|---------|--------------|-----------------|
| Mobile  | < 640px      | 100% - 32px     |
| Tablet  | 640 - 1024px | 100% - 48px     |
| Desktop | > 1024px     | 1280px (max)    |

### Layout Changes per Breakpoint

#### {Section: Header}

| Aspect        | Mobile                       | Tablet                       | Desktop                    |
|---------------|------------------------------|------------------------------|----------------------------|
| Height        | 56px                         | 64px                         | 72px                       |
| Layout        | Logo center, hamburger menu  | Logo left, collapsed nav     | Logo left, full nav        |
| Logo size     | 32px                         | 36px                         | 40px                       |
| Nav           | Hidden (drawer on hamburger) | Visible: 3-4 items           | All items + CTA button     |
| CTA Button    | Hidden                       | Hidden                       | Visible                    |

#### {Section: Hero}

| Aspect         | Mobile                   | Tablet                  | Desktop                  |
|----------------|--------------------------|-------------------------|--------------------------|
| Padding top    | 48px                     | 64px                    | 80px                     |
| Padding bottom | 48px                     | 64px                    | 80px                     |
| Layout         | Single column, centered  | Single column, centered | Two column (text + image)|
| Heading size   | Heading-2 (24px)         | Heading-1 (32px)        | 40px (custom)            |
| Image          | Below text               | Below text              | Right column             |
| CTA buttons    | Stacked                  | Side by side            | Side by side             |

#### {Section: Form}

| Aspect        | Mobile      | Tablet      | Desktop     |
|---------------|-------------|-------------|-------------|
| Width         | 100%        | 480px       | 480px       |
| Layout        | Full width  | Centered    | Centered    |

---

## Assets

### Icons

| Icon Name       | Library  | Size(s)      | Color                | Usage                  |
|-----------------|----------|--------------|----------------------|------------------------|
| eye             | Heroicons| 20px         | Neutral-400          | Show/hide password     |
| eye-slash       | Heroicons| 20px         | Neutral-400          | Hide password          |
| check-circle    | Heroicons| 20px         | Success-500          | Success indicators     |
| x-circle        | Heroicons| 20px         | Error-500            | Error indicators       |
| chevron-right   | Heroicons| 16px         | Current (inherit)    | Arrow indicators       |
| magnifying-glass| Heroicons| 20px         | Neutral-400          | Search input icon      |

**Icon style**: Outline (not solid) for most cases, solid for filled states
**Stroke width**: 1.5px

### Images

| Name         | Dimensions | Aspect Ratio | Format | Alt Text         | Notes               |
|--------------|------------|--------------|--------|------------------|---------------------|
| {hero-image} | 800×600px  | 4:3          | WebP   | {alt text here}  | Lazy load, preload on desktop |
| {avatar}     | 40×40px    | 1:1          | WebP   | User avatar      | Fallback: initials  |

### Illustrations

| Name              | Format | Color Mode      | Usage         |
|-------------------|--------|-----------------|---------------|
| {empty-state-svg} | SVG    | Themed (CSS var)| Empty state   |
| {error-svg}       | SVG    | Themed (CSS var)| Error pages   |

---

## Interaction Patterns

> Animation and transition specifications for interactive elements.

| Element           | Trigger     | Property   | Duration | Easing        |
|-------------------|-------------|------------|----------|---------------|
| Button            | hover       | background | 150ms    | ease-in-out   |
| Button            | hover       | shadow     | 150ms    | ease-in-out   |
| Input             | focus       | border     | 100ms    | ease          |
| Card              | hover       | shadow     | 200ms    | ease-out      |
| Dropdown          | open/close  | opacity+y  | 150ms    | ease-out      |
| Modal             | open        | opacity+scale| 200ms  | ease-out      |
| Toast             | appear      | opacity+y  | 200ms    | ease-out      |

---

## Validation Notes

> Notes for use during `/check-implementation` validation.
> List critical design decisions that are easy to miss or implement incorrectly.

1. **Touch targets**: All interactive elements must be at minimum 44×44px (mobile)
2. **Focus rings**: All focusable elements need visible focus ring (2px solid Primary-500, offset 2px)
3. **Color contrast**: Body text on white background must pass WCAG AA (4.5:1 ratio)
4. **Loading states**: Buttons must show spinner and be non-clickable during async operations
5. **Error messages**: Appear below input, not as alerts/toasts — inline only
6. {Add more critical notes specific to this design}

---

## Extraction Status

> Track which sections have been fully extracted (for large frames with iterative extraction).

- [ ] Frame overview and layout structure
- [ ] Design tokens (colors, typography, spacing)
- [ ] {Section 1} components
- [ ] {Section 2} components
- [ ] Responsive specifications
- [ ] Assets (icons, images)
- [ ] Interaction patterns
- [ ] Validation notes
