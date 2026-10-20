---
name: design-qa
description: Design QA for a FLIK prototype or page (dashboard or website) against the FLIK Design System. Checks missing states, spacing inconsistencies, colours, type, components, copy, responsive layout and accessibility, and reports findings with fixes. Use when asked to "design QA", "QA this prototype/page", "check states", "check spacing", "cek desain", or before calling a new prototype done.
---

# Design QA (FLIK)

Find what's wrong. Don't fix anything unless the user asks. Keep it cheap: let the two scripts do the scanning, and read the prototype only at the lines they point to (`sed -n 'A,Bp'`). Prefer JSON from `measure.js` over screenshots.

All paths are from the flik repo root. The scripts live in `design-system/skills/design-qa/scripts/`.

## 1. Scope

Which files and screens? Default: the files changed on this branch (`git diff --name-only main -- '*.html'`). For a dashboard menu, list its screens as URL hashes (see `design-system/dashboard/README.md`, e.g. `#shipments`, `#shipments/create` plus each step, the drawer, each modal).

## 2. Static pass (one command per file)

```bash
python3 design-system/skills/design-qa/scripts/design_qa.py product/Dashboard/<Menu>/prototype-v4.html
```

It checks colours against `tokens.json`, spacing against the 2px grid, radius/type/weight against values the design system uses, `:hover`/`:focus-visible`/disabled rules, traces of each content state, labels and alt text, copy and formats, and removed patterns. The per-menu files are copies of one app, so for a shared change run it on one file only.

Triage before reporting:
- Third-party marks keep their colours (bank, e-wallet, card, courier logos, a WhatsApp preview). Drop those hits.
- `#ffffff` typed instead of `var(--surface)`/`var(--on-primary)` is low priority; report it once as a count.

## 3. Browser pass

Start the `flik-root` preview (port 8766, serves the repo root). For each screen, at **1440×900** and then **375×812**, open it and run:

```js
eval(await (await fetch('/design-system/skills/design-qa/scripts/measure.js?'+Date.now())).text())
```

(If the page is served from somewhere else, paste the file's contents instead.) It returns: uneven gaps between repeated siblings, off-grid computed spacing, sideways page scroll, overflowing or clipped text, small tap targets, low-contrast text, the font sizes on screen, and unlabelled controls. Ignore hits from intentional decoration (connector lines, the prototype footer).

## 4. States matrix

For every screen, try to reach each state by clicking, typing and pressing Tab. Record ✓ (exists and looks right), ✗ (missing or broken) or n/a. A state you can't reach is a finding.

| State | What to look for |
|---|---|
| Default | Matches the design-system pattern for this page type (list, detail drawer, modal, FlowShell) |
| Hover / pressed | Every button, chip, tab, row and nav item reacts |
| Keyboard focus | Tab shows a visible ring on every control, in a sensible order; Esc closes drawers, modals, popovers |
| Selected / active | Tabs, rows, chips, options, nav item for the current page |
| Disabled | Primary action disabled until the form is valid (no error text in the footer); looks disabled, not just unclickable |
| Empty | A list with no data shows `EmptyState`, not an empty table |
| No results | A search or filter with no matches says so and offers to clear filters |
| Loading | Something shows while data or a submit is pending (skeleton rows, button spinner) |
| Error | A failed load or submit says what happened and offers retry; field errors sit under the field |
| Success | Toast in past tense or `SuccessBanner`, and the new item appears in the list |
| Content extremes | Long names and amounts (Rp1.250.000.000), one item vs many, pagination, missing optional data (shows "—") |
| Responsive | At 375px panels open as full-width drawers, tables scroll sideways, toolbars wrap cleanly, nothing scrolls the page sideways |

## 5. Spacing consistency

Beyond the script hits, compare the same thing across screens and pages: page padding, gap between page title and tabs, tabs and filter row, filter row and table, card padding, gap between cards (`grid-gap` 16px), form field spacing, modal and drawer padding. The same component must have the same spacing everywhere. Values should be on the 2px grid and already used in `components/bundle.css`.

## 6. Design-system rules

- Only token colours, no new tints, no gradients except the ribbon.
- Built from existing components (PageHeader, DataTable, FilterChip, Tabs, EmptyState, FlowShell, Modal, Toast …). A one-off card, button, badge, table or field is a finding; name the component it should be. If nothing fits, say "needs a new component (approval)".
- Never back: sidebar search, breadcrumbs, row chevrons, helper subtitles under titles, orange or gradient buttons, pastel card tiles.
- Copy: English first, sentence case, buttons say what happens, `Rp1.250.000`, `14 Oct 2026`, `+62 812-3456-7890`, AWB in mono, no exclamation marks or filler.

## 7. Report

Short, in chat, grouped by severity. Each finding gets one line: **what**, **where** (`file:line` or screen + selector), **fix** (the token, component or value to use).

- **P1:** breaks the design system or blocks use: missing state on a main flow, no keyboard focus, wrong colour, sideways scroll on phone, low contrast on body text.
- **P2:** visible inconsistency: off-grid or uneven spacing, one-off component, off-scale type, missing hover.
- **P3:** polish: typed hex that equals a token, copy nits.

End with the states matrix (screens × states) and a one-line verdict: ready, ready after P1 fixes, or not ready. Save it to a file only if the user asks (`product/<Product>/<Menu>/design-qa-YYYY-MM-DD.md`).

When the user then asks for fixes: change the per-menu `prototype-v4.html` files and refresh the copies as `AGENTS.md` describes, then rerun both scripts to confirm the hits are gone.
