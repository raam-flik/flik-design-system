# FLIK Design System for Tailwind CSS v4

The FLIK Design System as a Tailwind CSS v4 theme, with every component and the full merchant dashboard written in Tailwind utility classes.

| File | What it is |
|---|---|
| [`theme.css`](theme.css) | The FLIK theme (`@theme`): colours, type, corners, shadows, spacing. Generated from `../tokens.json` |
| [`index.html`](index.html) | Gallery of every component, rendered live, with its markup to copy |
| [`components/`](components/) | One file per component: plain Tailwind markup |
| [`dashboard/index.html`](dashboard/index.html) | The v4 merchant dashboard (Home, Transactions, Customers, Invoices, Shipments and the create flows) in Tailwind utilities |

## Set up

In your project's main CSS file:

```css
@import "tailwindcss";
@import "./theme.css";   /* copy tailwind/theme.css into your project */
```

Load the fonts in your HTML (or self-host them):

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

The gallery and the dashboard use Tailwind's browser build so they open without a build step. That is for previewing only; in a real project, build with the Tailwind CLI, Vite or PostCSS plugin as usual.

## The theme in one table

| Need | Use |
|---|---|
| The action colour | `bg-primary`, `text-primary`, `hover:bg-primary-hover`, `bg-primary-soft`, `disabled:bg-primary-disabled`, `text-on-primary` |
| Website text | `text-ink` (headings), `text-body`, `text-muted`, `text-faint` |
| Website grounds and lines | `bg-surface`, `bg-surface-alt`, `bg-dark`, `border-line`, `border-line-soft` |
| Dashboard text and lines | `text-app-ink`, `text-app-text`, `text-app-muted`, `text-app-faint`, `border-app-line`, `bg-app-hover`, `bg-app-field` |
| Status badges | `bg-badge-ok-bg text-badge-ok-text border-badge-ok-border` (also `warn`, `bad`, `info`, `neutral`) |
| Brand ribbon (glows only, never text) | `ribbon-1` orange, `ribbon-2` magenta, `ribbon-3` violet, `ribbon-4` cyan |
| Text styles (size, line height, weight, tracking together) | Website: `text-hero`, `text-display`, `text-heading`, `text-stat`, `text-title`, `text-lead`, `text-paragraph`, `text-label`, `text-button`, `text-caption`. Dashboard: `text-page-title`, `text-kpi`, `text-section-title`, `text-app-body`, `text-table-head`, `text-control`, `text-badge`. Code: `text-code` |
| Corners | `rounded-btn` (4px), `rounded-badge` (5px), `rounded-control` (6px), `rounded-card` (8px), `rounded-lg` (12px), `rounded-pill` |
| Shadows | Website: `shadow-sm`, `shadow-lg`, `shadow-hover`. Dashboard: `shadow-app` (cards, inputs, outline buttons), `shadow-pop` (menus, drawers, modals). Focus: `shadow-focus` |
| Layout sizes | `max-w-site` (1180px), `px-gutter`, `py-section`, `w-sidebar` (240px), `px-content`, `h-row` (52px table rows) |
| Fonts | `font-sans` (Inter), `font-mono` (JetBrains Mono) |

`text-paragraph` is the website body text size. It isn't called `text-body` because `body` is already a colour (`text-body`).

## The two rules still apply

1. **Reuse first.** Build from the components in `components/` before writing new markup. If something is missing, ask for it to be added to the design system first.
2. **Only FLIK colours.** `theme.css` switches Tailwind's default palette off (`--color-*: initial`), so classes like `bg-blue-500` or `text-gray-700` do nothing. The only hex values allowed in markup are third-party marks such as bank, e-wallet and courier logo colours (e.g. `bg-[#C8102E]`).

Copy is English first; money is written `Rp1.250.000` and left-aligned in tables; dates are `14 Oct 2026`.

## About the dashboard file

`dashboard/index.html` is converted automatically from the plain-CSS dashboard (`../dashboard/index.html`) and checked against it element by element on every page and flow: they render the same. A few things to know:

- **Every style is a utility class in the markup.** States use variants: `hover:`, `disabled:`, `[&.on]:` (a state class the script adds), `[.grp.open_&]:` (styled by a parent), `max-[960px]:` (phones).
- **The original class names stay** (`nav`, `tab`, `sx-ship`, `on`, `open` …). They carry no styles; the JavaScript uses them to find elements and to switch states.
- **A short `@layer base` block** styles bare elements the script creates without classes (`table`, `th`, `td`, `h1`, page text).
- To regenerate it after the dashboard changes: `python3 scripts/convert_dashboard_to_tailwind.py`.

## Regenerate

```bash
python3 scripts/build_tailwind.py                 # theme.css and the gallery, from tokens.json and components/
python3 scripts/convert_dashboard_to_tailwind.py  # dashboard/index.html, from ../dashboard/index.html
```
