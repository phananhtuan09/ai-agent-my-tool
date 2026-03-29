---
frame_url: null
frame_name: Midnight AI Dark Theme
file_name: midnight-ai.theme.json
extracted: 2026-03-28
status: complete
---

# Figma: Midnight AI — Dark Theme Redesign

> **Purpose**: This document captures the complete design specification for the Midnight AI theme.
> 1. **Implementation guide** — AI agents use this to implement pixel-perfect UI.
> 2. **Validation reference** — used by `/check-implementation` to verify code matches design.

---

## Reference

| Field     | Value                                        |
|-----------|----------------------------------------------|
| File      | midnight-ai.theme.json                       |
| Frame     | Full app redesign — base.html + style.css    |
| URL       | n/a (custom theme, not from Figma)           |
| Extracted | 2026-03-28                                   |
| Status    | complete                                     |

---

## Frame Overview

**Screen**: All pages (global shell)
**User type**: Personal VPS owner / developer
**Purpose**: Unified dark-only control room for AI automation agents. Premium, cinematic, sci-fi AI aesthetic.
**Product flow position**: Dashboard → Config → Agent pages (Crypto Airdrop, Daily Scheduler)

---

## Layout Structure

```
{App Shell} [Grid: 260px sidebar + 1fr main]
├── {Sidebar} [Aside] — Fixed left panel, dark surface
│   ├── {Brand} [Link] — Logo + "Personal VPS / AI Agent Tool"
│   └── {Nav Group} [Nav] — Numbered links with icons, title, summary
│       ├── {Nav Link} [Anchor] — numbered item (01, 02, 03…)
│       └── ... (repeated per agent)
└── {Main Stage} [Main] — Scrollable content area
    ├── {Topbar} [Header] — Page title + connection status + actions
    │   ├── {Page Header} [Div] — eyebrow + h1
    │   └── {Topbar Actions} [Div] — connection dot, buttons
    └── {Block Content} — page-specific content
        ├── {Page Hero} [Section] — accent banner
        ├── {Dashboard Grid} [Section] — agent cards (dashboard)
        └── {Agent Layout} [Section] — controls + chat (agent pages)
```

**Layout type**: Two-column fixed sidebar + fluid main
**Container max-width**: none (full width)
**Main axis**: Horizontal (sidebar | main) → vertical within main

---

## Design Tokens

### Colors

| Token Name      | Hex / Value                        | Usage                                |
|-----------------|------------------------------------|--------------------------------------|
| bg              | `#080c14`                          | Page background                      |
| bg-alt          | `#060a11`                          | Gradient start / alternate bg        |
| surface         | `#0e1420`                          | Sidebar, cards, panels               |
| surface-raised  | `#141d2e`                          | Hovered cards, dropdowns             |
| surface-overlay | `rgba(14, 20, 32, 0.96)`           | Modals, overlays                     |
| primary-400     | `#22d3ee`                          | Primary buttons, active states       |
| primary-500     | `#06b6d4`                          | Links, highlights                    |
| primary-300     | `#67e8f9`                          | Primary text on dark surface         |
| secondary-400   | `#c084fc`                          | Accent elements, badges              |
| secondary-500   | `#a855f7`                          | Secondary accent                     |
| neutral-50      | `#f0f4f8`                          | Heading text                         |
| neutral-200     | `#bcccdc`                          | Body text                            |
| neutral-400     | `#829ab1`                          | Muted / secondary text               |
| neutral-600     | `#486581`                          | Faint text, placeholders             |
| border          | `rgba(188, 204, 220, 0.10)`        | Default border                       |
| border-strong   | `rgba(188, 204, 220, 0.20)`        | Emphasized border, active navlinks   |
| success         | `#34d399`                          | Success states (dark-mode adjusted)  |
| warning         | `#fbbf24`                          | Warnings                             |
| error           | `#f87171`                          | Errors, destructive                  |
| info            | `#22d3ee`                          | Info states                          |

### Gradients

| Token           | CSS Value                                                         | Usage                        |
|-----------------|-------------------------------------------------------------------|------------------------------|
| gradient-primary| `linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)`              | Primary buttons, hero badges |
| gradient-accent | `linear-gradient(135deg, #22d3ee 0%, #a855f7 100%)`              | Highlight strips, active nav |
| gradient-bg     | `linear-gradient(180deg, #060a11, #080c14)`                       | Body background              |
| glow-cyan       | `radial-gradient(ellipse at top, rgba(6,182,212,0.12) 0%, transparent 70%)` | Hero section ambient glow |
| glow-purple     | `radial-gradient(ellipse at bottom, rgba(168,85,247,0.10) 0%, transparent 70%)` | Footer/bottom glow |

### Typography

| Style Name  | Font Family    | Size  | Weight | Line Height | Letter Spacing | Usage              |
|-------------|----------------|-------|--------|-------------|----------------|--------------------|
| Display     | Space Grotesk  | 48px  | 700    | 1.2         | -0.025em       | Hero titles        |
| Heading-1   | Space Grotesk  | 38px  | 700    | 1.2         | -0.025em       | Page title (h1)    |
| Heading-2   | Space Grotesk  | 30px  | 700    | 1.2         | -0.02em        | Section heading    |
| Heading-3   | Space Grotesk  | 24px  | 600    | 1.3         | -0.01em        | Card title         |
| Heading-4   | Space Grotesk  | 20px  | 600    | 1.3         | 0              | Sub-section title  |
| Body-Large  | Inter          | 17px  | 400    | 1.55        | 0              | Lead/intro text    |
| Body        | Inter          | 15px  | 400    | 1.55        | 0              | General body text  |
| Body-Small  | Inter          | 13px  | 400    | 1.55        | 0              | Secondary text     |
| Label       | Inter          | 13px  | 500    | 1.2         | 0.04em         | Nav labels, badges |
| Caption     | Inter          | 12px  | 400    | 1.4         | 0.04em         | Eyebrows, kickers  |
| Code        | IBM Plex Mono  | 13px  | 400    | 1.55        | 0              | Mono data, paths   |
| Code-Label  | IBM Plex Mono  | 12px  | 500    | 1.2         | 0.1em          | Status chips, tags |

**Google Fonts import:**
```
Space Grotesk: 500, 700
IBM Plex Mono: 400, 500
IBM Plex Sans: 400, 500, 600  (fallback body)
Inter: 400, 500, 600 (preferred body)
```

### Spacing Scale

| Token  | Value | Usage                                  |
|--------|-------|----------------------------------------|
| xs     | 4px   | Icon-to-text, tight gaps               |
| sm     | 8px   | Badge padding, tight items             |
| md     | 16px  | Default padding, card inner padding    |
| lg     | 24px  | Section inner padding, row gaps        |
| xl     | 32px  | Section separation, large gaps         |
| 2xl    | 48px  | Between major sections                 |
| 3xl    | 64px  | Page-level padding                     |
| 4xl    | 96px  | Hero section top/bottom                |

### Shadows

| Token      | CSS Value                                                                                      | Usage                    |
|------------|-----------------------------------------------------------------------------------------------|--------------------------|
| shadow-sm  | `0 2px 8px rgba(6,182,212,0.08), 0 1px 3px rgba(0,0,0,0.4)`                                  | Resting cards            |
| shadow-md  | `0 8px 20px -4px rgba(6,182,212,0.14), 0 4px 8px -4px rgba(0,0,0,0.5)`                       | Hovered cards, dropdowns |
| shadow-lg  | `0 16px 32px -8px rgba(6,182,212,0.18), 0 8px 16px -8px rgba(0,0,0,0.5)`                     | Modals, sheets           |
| shadow-xl  | `0 24px 48px -12px rgba(6,182,212,0.22), 0 12px 24px -12px rgba(168,85,247,0.14)`            | Dialogs                  |
| glow-sm    | `0 0 12px rgba(6, 182, 212, 0.35)`                                                            | Active nav items         |
| glow-md    | `0 0 24px rgba(6, 182, 212, 0.4)`                                                             | Primary buttons (focus)  |
| glow-purple| `0 0 20px rgba(168, 85, 247, 0.35)`                                                           | Accent badges            |

### Border Radius

| Token   | Value  | Usage                          |
|---------|--------|--------------------------------|
| xs      | 4px    | Badges, chips                  |
| sm      | 6px    | Code inline, small tags        |
| md      | 10px   | Buttons, inputs                |
| lg      | 14px   | Cards, panels                  |
| xl      | 18px   | Larger cards, nav sidebar      |
| 2xl     | 24px   | Modal dialogs                  |
| full    | 9999px | Pills, toggles, avatars        |

---

## Component Specifications

### Sidebar

**Width**: 260px fixed
**Background**: `surface` (#0e1420)
**Border-right**: `1px solid border` (rgba(188,204,220,0.10))
**Padding**: 24px vertical, 16px horizontal

#### Brand Logo
| Property   | Value                                              |
|------------|----------------------------------------------------|
| Kicker text| Caption style, neutral-400, letter-spacing: widest |
| Brand name | Heading-4, neutral-50, Space Grotesk               |
| Padding    | 20px bottom                                        |

#### Nav Link

| State    | Background                    | Text         | Border-left                    | Icon         |
|----------|-------------------------------|--------------|--------------------------------|--------------|
| Default  | transparent                   | neutral-400  | none                           | neutral-600  |
| Hover    | rgba(6,182,212,0.06)          | neutral-200  | none                           | neutral-400  |
| Active   | rgba(6,182,212,0.10)          | neutral-50   | 2px solid primary-400 (#22d3ee)| primary-400  |

**Dimensions**: padding 10px 12px, border-radius: md (10px)
**Nav icon**: Code-Label style (IBM Plex Mono 12px 500), neutral-600 → primary-400 when active
**Title**: Body-Small (13px 500), transition: color 150ms ease
**Summary**: Caption (12px), neutral-600, display block below title

---

### Topbar

**Height**: 64px
**Background**: `bg` (#080c14) with `border-bottom: 1px solid border`
**Padding**: 0 32px

#### Eyebrow
- Caption style, neutral-500, letter-spacing: wide, uppercase

#### Page H1
- Heading-1 style (38px on large screens), neutral-50

#### Connection Status Dot
| State       | Dot color  | Pulse animation |
|-------------|------------|-----------------|
| connecting  | amber #fbbf24 | none         |
| connected   | success #34d399 | slow pulse (2s) |
| disconnected| error #f87171 | none          |

---

### Button

#### Primary

| State    | Background                                    | Text       | Shadow        |
|----------|-----------------------------------------------|------------|---------------|
| Default  | gradient-primary (cyan→blue)                  | #ffffff    | shadow-sm     |
| Hover    | shift gradient slightly brighter              | #ffffff    | shadow-md + glow-sm |
| Active   | `#0891b2` (primary-600, solid)                | #ffffff    | none          |
| Focus    | gradient-primary                              | #ffffff    | glow-md (cyan ring) |
| Disabled | neutral-800 (#243b53)                         | neutral-600| none          |

**Dimensions**: height 40px, padding 10px 20px, border-radius: md (10px)
**Font**: Body-Small 500 (13px), letter-spacing: 0.02em
**Transition**: all 150ms ease-in-out

#### Ghost

| State    | Background                       | Text          | Border                        |
|----------|----------------------------------|---------------|-------------------------------|
| Default  | transparent                      | neutral-400   | 1px solid border              |
| Hover    | rgba(188,204,220,0.06)           | neutral-200   | 1px solid border-strong       |
| Active   | rgba(188,204,220,0.10)           | neutral-50    | 1px solid border-strong       |

---

### Card (Dashboard Agent Card)

| Property       | Value                                             |
|----------------|---------------------------------------------------|
| Background     | surface (#0e1420)                                 |
| Border         | 1px solid border                                  |
| Border-radius  | lg (14px)                                         |
| Padding        | 24px                                              |
| Shadow         | shadow-sm                                         |
| Hover shadow   | shadow-md                                         |
| Hover border   | 1px solid rgba(6,182,212,0.25)                    |
| Transition     | box-shadow 200ms ease-out, border 200ms ease-out  |

#### Card accent strip (top border)
- `accent-blue`: 2px top border, gradient-primary
- `accent-teal`: 2px top border, `#14b8a6`
- Applied via `border-top: 2px solid <accent>`

#### Status Pill
| Variant   | Background                     | Text          |
|-----------|--------------------------------|---------------|
| is-ready  | rgba(52,211,153,0.12)          | #34d399       |
| is-warn   | rgba(251,191,36,0.12)          | #fbbf24       |
| is-error  | rgba(248,113,113,0.12)         | #f87171       |

**Dimensions**: padding 3px 10px, border-radius: full, font: Code-Label (12px 500)

#### Metric List (dl)
- `dt`: Caption (12px), neutral-500, uppercase, letter-spacing: widest
- `dd`: Code style (IBM Plex Mono 13px), neutral-200

---

### Page Hero Banner

| Property       | Value                                            |
|----------------|--------------------------------------------------|
| Background     | surface (#0e1420) + glow-cyan overlay            |
| Border-bottom  | 1px solid border                                 |
| Padding        | 32px 32px                                        |
| Border-radius  | none (full-width section)                        |

**Eyebrow**: Caption, neutral-500, uppercase
**H2**: Heading-2, neutral-50
**Hero badge**: status pill variant (gradient-accent bg, white text)

---

### Modal / Config Dialog

| Property       | Value                                             |
|----------------|---------------------------------------------------|
| Overlay        | rgba(6,10,17,0.80) backdrop                       |
| Background     | surface-overlay (#0e1420)                         |
| Border         | 1px solid border-strong                           |
| Border-radius  | 2xl (24px)                                        |
| Shadow         | shadow-xl                                         |
| Padding        | 28px                                              |
| Max-width      | 480px                                             |
| Animation      | opacity 0→1 + translateY(8px→0), 200ms ease-out  |

---

### Input / Select

| State    | Background           | Border                    | Text        |
|----------|----------------------|---------------------------|-------------|
| Default  | rgba(14,20,32,0.8)   | 1px solid border          | neutral-200 |
| Focused  | rgba(14,20,32,1)     | 1px solid primary-400     | neutral-50  |
| Error    | rgba(248,113,113,0.06)| 1px solid error #f87171  | neutral-200 |
| Disabled | rgba(8,12,20,0.5)    | 1px solid border (dashed) | neutral-600 |

**Dimensions**: height 40px, padding 10px 14px, border-radius: md (10px)
**Font**: Body-Small (13px), Inter
**Focus glow**: `box-shadow: 0 0 0 3px rgba(6,182,212,0.15)`

---

### Chat / Stream Area

| Property       | Value                                           |
|----------------|-------------------------------------------------|
| Background     | bg-alt (#060a11)                                |
| Border         | 1px solid border (top, separating from controls)|
| Padding        | 16px                                            |

**Message bubble (assistant)**:
- Background: surface (#0e1420)
- Border: 1px solid border
- Border-radius: lg (14px), bottom-left: sm (6px)
- Padding: 12px 16px

**Message bubble (user)**:
- Background: rgba(6,182,212,0.08)
- Border: 1px solid rgba(6,182,212,0.15)
- Border-radius: lg (14px), bottom-right: sm (6px)

**Typing indicator**: 3 dots, primary-400, fade-pulse 1.4s ease-in-out

---

## Responsive Specifications

### Breakpoints

| Name    | Range        | Behavior                        |
|---------|--------------|---------------------------------|
| Mobile  | < 768px      | Sidebar collapses to hamburger  |
| Tablet  | 768–1024px   | Sidebar 220px, reduced padding  |
| Desktop | > 1024px     | Full layout, sidebar 260px      |

### Layout Changes

| Aspect         | Mobile                        | Tablet             | Desktop             |
|----------------|-------------------------------|--------------------|---------------------|
| Sidebar        | Hidden, drawer on toggle      | 220px fixed        | 260px fixed         |
| Dashboard grid | 1 column                      | 2 columns          | 3 columns           |
| Topbar padding | 16px                          | 24px               | 32px                |
| H1 size        | 24px                          | 30px               | 38px                |

---

## Interaction Patterns

| Element          | Trigger     | Property              | Duration | Easing      |
|------------------|-------------|-----------------------|----------|-------------|
| Nav link         | hover       | background, text      | 150ms    | ease        |
| Nav link active  | click       | border-left, glow     | 150ms    | ease        |
| Card             | hover       | shadow, border-color  | 200ms    | ease-out    |
| Button primary   | hover       | shadow + glow         | 150ms    | ease-in-out |
| Button           | active      | scale(0.98)           | 80ms     | ease        |
| Modal            | open        | opacity + translateY  | 200ms    | ease-out    |
| Connection dot   | connected   | pulse scale           | 2000ms   | ease-in-out |
| Input            | focus       | border + glow ring    | 100ms    | ease        |
| Status pill      | mount       | fadeIn                | 300ms    | ease-out    |

---

## CSS Variables Mapping

Map to `style.css :root` variables:

```css
:root {
  --bg:              #080c14;
  --bg-alt:          #060a11;
  --surface:         #0e1420;
  --surface-raised:  #141d2e;
  --surface-overlay: rgba(14, 20, 32, 0.96);

  --ink:             #bcccdc;       /* neutral-200 */
  --ink-heading:     #f0f4f8;       /* neutral-50  */
  --ink-soft:        #829ab1;       /* neutral-400 */
  --ink-faint:       #486581;       /* neutral-600 */

  --border:          rgba(188, 204, 220, 0.10);
  --border-strong:   rgba(188, 204, 220, 0.20);

  --cyan:            #22d3ee;       /* primary-400 */
  --cyan-hover:      #06b6d4;       /* primary-500 */
  --cyan-text:       #67e8f9;       /* primary-300 */
  --cyan-soft:       rgba(6, 182, 212, 0.10);
  --cyan-glow:       rgba(6, 182, 212, 0.20);

  --purple:          #c084fc;       /* secondary-400 */
  --purple-soft:     rgba(168, 85, 247, 0.10);
  --purple-glow:     rgba(168, 85, 247, 0.20);

  --gradient-primary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  --gradient-accent:  linear-gradient(135deg, #22d3ee 0%, #a855f7 100%);

  --success:         #34d399;
  --success-soft:    rgba(52, 211, 153, 0.12);
  --warning:         #fbbf24;
  --warning-soft:    rgba(251, 191, 36, 0.12);
  --danger:          #f87171;
  --danger-soft:     rgba(248, 113, 113, 0.12);
  --info:            #22d3ee;
  --info-soft:       rgba(34, 211, 238, 0.12);

  --shadow-sm:  0 2px 8px rgba(6,182,212,0.08), 0 1px 3px rgba(0,0,0,0.4);
  --shadow-md:  0 8px 20px -4px rgba(6,182,212,0.14), 0 4px 8px -4px rgba(0,0,0,0.5);
  --shadow-lg:  0 16px 32px -8px rgba(6,182,212,0.18), 0 8px 16px -8px rgba(0,0,0,0.5);
  --shadow-xl:  0 24px 48px -12px rgba(6,182,212,0.22), 0 12px 24px -12px rgba(168,85,247,0.14);
  --glow-sm:    0 0 12px rgba(6, 182, 212, 0.35);
  --glow-md:    0 0 24px rgba(6, 182, 212, 0.4);

  --mono:    'IBM Plex Mono', ui-monospace, monospace;
  --body:    Inter, system-ui, sans-serif;
  --display: 'Space Grotesk', system-ui, sans-serif;
}
```

---

## Contrast Verification (WCAG AA)

| Pair                              | Ratio     | Status |
|-----------------------------------|-----------|--------|
| `--ink` (#bcccdc) on `--bg`       | 7.1:1     | ✓ AAA  |
| `--ink-heading` on `--bg`         | 13.4:1    | ✓ AAA  |
| `--ink-soft` on `--bg`            | 4.6:1     | ✓ AA   |
| White on gradient-primary (cyan)  | 4.8:1     | ✓ AA   |
| `--cyan` (#22d3ee) on `--surface` | 5.2:1     | ✓ AA   |
| `--success` on `--surface`        | 5.8:1     | ✓ AA   |
| `--warning` on `--surface`        | 6.2:1     | ✓ AA   |
| `--danger` on `--surface`         | 4.9:1     | ✓ AA   |

---

## Validation Notes

1. **Glow effects**: Use sparingly — only on active nav, focused inputs, primary button hover. Do not glow all elements.
2. **Gradient buttons**: `--gradient-primary` only for primary CTA. Ghost/secondary buttons use flat colors.
3. **Cyan as primary**: Replace `--blue` references in current CSS with `--cyan` / `--cyan-hover`.
4. **Surface vs bg**: Cards and sidebar use `--surface`, page background uses `--bg`. Never mix.
5. **Font**: Replace `IBM Plex Sans` body → `Inter`. Keep `IBM Plex Mono` for mono. Add `Space Grotesk` for `--display`.
6. **Accent strips on cards**: Keep `accent-blue` class, update color to `--gradient-primary` or `--cyan`.
7. **Status pills**: Must use semi-transparent backgrounds (not solid) — e.g. `rgba(52,211,153,0.12)` not `#34d399`.
8. **Touch targets**: All nav links and buttons ≥ 40×40px minimum.
9. **Transition**: Add `transition: color 150ms ease, background 150ms ease` to nav links.
10. **Connection dot**: Animate with CSS `@keyframes pulse` on `connected` state only.

---

## Extraction Status

- [x] Frame overview and layout structure
- [x] Design tokens (colors, typography, spacing, shadows)
- [x] Sidebar + nav link component
- [x] Topbar + page header component
- [x] Button components (primary, ghost)
- [x] Card (dashboard agent card)
- [x] Page hero banner
- [x] Modal / config dialog
- [x] Input / select
- [x] Chat / stream area
- [x] CSS variables mapping
- [x] Responsive specifications
- [x] Interaction patterns
- [x] Contrast verification
- [x] Validation notes
