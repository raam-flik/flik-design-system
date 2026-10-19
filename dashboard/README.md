# Reference dashboard

**Live:** https://landing-page-raams-projects-2709477f.vercel.app/dashboard/

This is a **copy**. The main copy lives in the flik-dashboard repo (`product/Dashboard/<menu>/prototype-v4.html`, one file per menu); change it there first, then refresh this file.

`index.html` is the newest FLIK merchant dashboard prototype (v4 palette) as one self-contained file: HTML, CSS and JavaScript inline, no build step, no dependencies except the Inter font from Google Fonts. Open it in a browser or serve the folder (`python3 -m http.server`) and start from it when you build a new page. All data in it is made up and seeded, so it looks the same on every load.

## Pages

| URL hash | Page | What it shows |
|---|---|---|
| `#home` | Home | Quick access tiles and the sales chart |
| `#transactions` | Transactions | Tabs, filter chips, table with bulk select, detail drawer, refund modal, CSV export |
| `#customers` | Customers | The `EmptyState` pattern (nothing to list yet) |
| `#invoices` | Invoices | `PageHeader`, tabs, filter chips, table |
| `#invoices/create` | Create invoice | Full-screen editor: form left, live PDF / WhatsApp / payment page preview right |
| `#shipments` | Shipments | List with status tabs |
| `#shipments/create` | Create shipment | Five-step flow (Details, Courier, Pickup, Summary, Payment) with a running summary and a success screen |

## How the file is organised

Everything is in order inside the one file; search for the `/* ===== … ===== */` headings.

- **Tokens** (top of `<style>`): `--primary`, `--ink`, `--text`, `--muted`, `--line`, `--hover`, `--sh` (card shadow), `--pop` (popover shadow) and the status badge colours. These match `tokens.json` (`app-*` names) in this repo.
- **Layout and components CSS**: sidebar, top bar, tabs, filter chips, buttons (`.btn-p`, `.btn-o`, `.btn-d`), table, drawer, modal, toast, then one block per page (Home, Invoices, Shipments). The design system's `components/bundle.css` has the same patterns with `fl-` class names.
- **Markup**: one `<main class="content" id="view-…">` per page, plus the full-screen editors (`#ie` for invoices, `#sx` for shipments), the popover `#pop`, the modal `#mscrim` / `#modal` and the toast.
- **Icons**: the `P` map of 24px line icons and `ic(name, size, stroke)`, which returns an inline SVG.
- **Sidebar**: the `NAV` array. An item with `v:'key'` opens a page; a sub-item can be a string (shows a toast) or `{t:'Invoices', v:'inv'}` (opens a page).
- **Data**: seeded dummy data (`rnd()`, `pick()`), formatting helpers `rp()` (Rp1.250.000), `fdate()` and `fday()` (14 Oct 2026).
- **Shared helpers**: `toast(text)`, `placePop(anchor)` / `closePop()` for popovers, `modal` + `mscrim` + `closeModal()` for dialogs. Any element with `data-toast="…"` shows that toast when clicked.
- **Router** (end of the script): `VIEWS` maps a page key to its hash and title, and `show(view)` switches pages, opens the create flows on `#…/create` and highlights the sidebar.

## Adding a page

1. Add a `<main class="content" id="view-yourkey" hidden>` with an `h1` (or a `PageHeader` row).
2. Add `yourkey:['your-hash','Your title']` to `VIEWS`.
3. Point a sidebar item at it with `v:'yourkey'` in `NAV`.
4. If it needs data or rendering, write a `renderYourPage()` and call it from `show()`.

Formats: money `Rp1.250.000` (no space, left-aligned in tables, no currency column), dates `14 Oct 2026`, phone `+62 812-3456-7890`. Courier logos load from the live site.
