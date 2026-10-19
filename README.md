# FLIK Design System

Tokens, components and guidelines for the FLIK marketing site and merchant dashboard (v4 palette: navy #002D5D, violet #6A4BFF, cyan #00E5FF, magenta #FF2DB8, orange #FF7A2E).

**Live, browsable version:** the FLIK Design System on claude.ai (ask the design team for access).

## What's in this repo

| Path | What |
|---|---|
| `tokens.json` | Every colour, type style, spacing, radius and shadow token, with a usage note each |
| `tokens.css` | The same tokens as CSS custom properties and type classes (generated from `tokens.json`) |
| `components/bundle.css` | Component styles; every class starts with `fl-` |
| `components/<Name>/preview.html` | A live example of each component (markup to copy) |
| `components/<Name>/README.md` | When to use it, how it behaves, what not to do |
| `assets/Logos/` | The real FLIK wordmark and F mark. Never redraw them |
| `dashboard/index.html` | The newest merchant dashboard prototype as one HTML file, to reuse its structure ([guide](dashboard/README.md)) |

## Reference dashboard

The newest dashboard built with this system: **https://landing-page-raams-projects-2709477f.vercel.app/dashboard/**

Its full HTML is in [`dashboard/index.html`](dashboard/index.html), one self-contained file you can copy to start a new page. [`dashboard/README.md`](dashboard/README.md) explains its pages, how the file is organised and how to add a page.

## Quick start

```html
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="components/bundle.css">
<div class="fl fl-app">
  <button class="fl-abtn fl-abtn--primary">Create invoice</button>
</div>
```

The previews expect `tokens.css` and `bundle.css` to be loaded first; open them through a page that links both.

FLIK is commerce infrastructure for Indonesian brands: **Payment** (Checkout, In-Store Payment, Invoice, Payment Link), **Shipping** (every courier in one dashboard, across Indonesia, Malaysia and Singapore) and **Funding** (Merchant Cash Advance). This system covers both places merchants meet FLIK: the **marketing site** and the **merchant dashboard**. They share one accent, one type family and one set of formats; each has its own neutrals and density, so tokens and components are split into a Marketing layer and a Product layer (`app-` prefix).

## Content fundamentals

- **Plain, short, specific.** Write the way a helpful account manager talks. Lead with the outcome and the number: "Checkout in 30 seconds.", "Every courier, one dashboard. Up to 40% less.", "One fixed margin, no hidden fees."
- **You and your.** Speak to the merchant ("your balance", "your shoppers"). FLIK refers to itself as FLIK or "the FLIK team", never "we" in headings.
- **Sentence case** everywhere: headings, buttons, menu items ("Contact sales", "Start shipping free"). Product names keep their capitals (Checkout, Merchant Cash Advance, FLIK Account).
- **Languages.** English first at `/`, Bahasa Indonesia second at `/id/` with the same slugs. Dashboard menu names stay Indonesian where merchants know them: Personalisasi Checkout, Laporan & Analisis, Pengaturan Pengiriman.
- **Formats.** Money `Rp1.250.000` (no space, no decimals, dot thousands); short money `Rp250 jt`, `Rp5 M`; amounts in tables are left-aligned with no currency column; dates `14 Okt 2026`, with time `14 Okt 2026, 10:42`; phone `+62 812-3456-7890`; AWB numbers in the mono face.
- **Only real claims.** Use the figures in the product reference (30-second checkout, 3× faster, 40% off shipping, 3% COD fee, 99% shipment creation success). Mark example data in mockups as example data.
- **Buttons say what happens** ("Refund", "Create shipments"); toasts confirm in past tense ("Refund sent").
- No emoji, no exclamation marks in UI, no "revolutionary", "seamless" or other filler.

## Visual foundations

**Colour.** The palette is navy #002D5D (`ink`, `dark`), violet #6A4BFF (`primary`), cyan #00E5FF, magenta #FF2DB8 and orange #FF7A2E. `primary` (#6A4BFF) is the only action colour on both layers: buttons, links, active tabs, selection and focus. Its tint `primary-soft` sits behind violet text. Text on violet is `on-primary`.
- Marketing text: `ink` for headings, `body` for paragraphs, `muted` for leads and the soft half of section headings, `faint` only for 13px+ labels. Grounds are `surface` and `surface-alt`; one `dark` band per page at most (Developers, COD), with `dark-raised` cards and `on-dark-muted` text.
- Product text: `app-ink` titles and amounts, `app-text` body, `app-muted` secondary, `app-faint` counts and hints only (12px+). Hover rows `app-hover`, selected rows `app-selected`, the search and segmented track `app-field`.
- Status: marketing pills use `ok-soft`/`ok-text`, `warn-soft`/`warn-text`, `bad-soft`/`bad-text`, `primary-soft`/`primary`; dashboard badges use the `badge-*` sets (fill, text, border). Every status also carries its word.
- `flik-orange` and `flik-navy` belong to the logo only. The ribbon runs orange → magenta → violet → cyan (`ribbon-1` to `ribbon-4`), with orange holding for its first ~40%. Ribbon stops are for the hero wave and soft glows behind mockups, never for text, buttons or cards.
- `faint` and `app-faint` are under 4.5:1 on white: keep them for non-essential labels at 12–13px and up.

**Type.** One family, Inter, plus JetBrains Mono for code, AWB numbers and step counters.
- Marketing headings are light and large: `hero` (60px/400) on the homepage, `display` (56px/300) on product pages, `heading` (36px/300) for sections, `stat` (48px/300) for numbers. Body is `body` (15px/1.6), leads are `lead` (20px/300 in `muted`), labels are `label` (14px/500).
- Product type is smaller and heavier: `page-title` (28px/600), `section-title` (18px/600), `app-body` (14px), `table-head` (13.5px/600), `control` (13.5px/500), `badge` (12.5px/500).
- Use tabular figures (`.num`) for every amount and count.

**Layout (marketing).** Content sits in a `container` of 1180px with a 32px `gutter` (16px on phones). Two vertical guide lines in `guide` frame every section 1266px apart, from header to footer; ruled grids and bands stretch exactly to those lines. Sections breathe: `section-y` 112px (72px on phones). Heroes are either split (text left, live demo right) or centred (text above a full-width visual).

**Layout (product).** A 240px sidebar (`app-sidebar`), a sticky top bar with search, notifications, settings and a violet Create button, and content padded `app-content-x` (28px). Lists follow one pattern: page title, underline tabs, a filter row (search, filter chips, sort, Export, then the primary action), the table, then pagination. Rows open a 460px detail drawer from the right; short tasks open a 440px modal. Creating something opens a full-screen flow (`FlowShell`): an editor with a live preview for invoices, or numbered steps with a running summary for shipments. A list with no data yet shows an `EmptyState`.

**Shape and depth.**
- Radii: `radius-btn` 4px for marketing buttons, `radius-control` 6px for dashboard controls, `radius-card` 8px for windows and dashboard cards, `radius-lg` 12px for marketing cards, menus and modals, `radius-pill` for pills and chips, `radius-badge` 5px for status badges.
- Marketing depth: `shadow-sm` on small cards, `shadow-lg` on mockup windows and menus, `shadow-hover` when a card lifts.
- Product depth: every card, input and outline button uses `app-shadow` (a 1px ring plus a soft drop) instead of a border; floating things use `app-pop`.

**Focus.** Marketing buttons show `focus-ring` (3px of `primary` at 35%); dashboard fields show a 2px ring at 40%. Never remove focus without a replacement.

**Motion.** Small and purposeful. Buttons lift 1px on hover and sink on press; the hover arrow grows a stem and slides 3px. Product mockups on marketing pages play their own flow on a loop (typing, selection, a count-up), pause when off screen, and stop under `prefers-reduced-motion`. The hero ribbon waves slowly. No parallax, no confetti.

**Imagery.** Show the product, not stock photos: mockups are built from these components with realistic Indonesian data (Aruna Studio, QRIS, JNE Reguler, Rp amounts) and marked as examples. Real merchant logos only with permission. A testimony photo must be of the real person.

## Iconography

Line icons on a 24px grid, 1.7px stroke (2px at 14px and below), round caps and joins, drawn with `currentColor` so they take the text colour. Sizes: 18px in marketing tiles, 16px in dashboard navigation and menus, 14–15px inside chips and pills. Icon tiles are 32–40px with `primary-soft` fill and `primary` icon. No emoji and no filled or duotone icon sets.

## Logo

Use the files in **Logos**; never redraw them. The wordmark goes top-left in every header (30px tall on marketing, the F mark at 16–28px in the dashboard account switcher and app icons). Keep clear space of at least the height of the F around the logo. Put it on `surface` or `surface-alt` only; on the `dark` band use the F mark alone on a white tile.

## Sitemap (Products menu)

Three columns, always in this order:

| Payment | Shipping | Funding |
|---|---|---|
| Payment | Shipping | Merchant Cash Advance |
| In-Store Payment | Bulk Shipping | Auto Settlement |
| Checkout | COD Shipping | Flexibility |
| Invoice | Shipment Tracking | Inventory Financing |
| Payment Link | Courier Performance | Outlet Expansion |
| Payment Methods | Warehouses | Marketing Budget |
| FLIK Account | Return Management | |
| Checkout Personalization | Cross-Border Shipping | |

## Using the components

Load `tokens.css`, then `components/bundle.css`. Every class starts with `fl-`. Wrap marketing markup in `.fl` and dashboard markup in `.fl fl-app` so each gets its base text style. Components are plain HTML and CSS; copy the markup from each component's preview and add your own behaviour (open/close, sorting). Marketing components: Button, TextLink, Pill, SectionHeading, StatGrid, ResourceCard, FAQ, Header, CodePanel. Product components: AppButton, StatusBadge, FilterChip, Tabs, SegmentedControl, DataTable, KPICard, FormField, Checkbox, PopoverMenu, Modal, Toast, SidebarNav, SearchField. Product flows (the v4 Customers, Invoices and Shipments pages): PageHeader, EmptyState, FlowShell, Stepper, OptionCard, RadioList, ChoicePills, Combobox, EntityCard, LineItems, CollapsibleCard, CourierServiceCard, SummaryPanel, PaymentCards, DocumentPreview, SuccessBanner.

Do not add back: sidebar search, breadcrumbs, row chevrons, helper subtitles under titles, orange or gradient buttons, pastel card tiles.
