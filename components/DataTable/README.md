# DataTable

The dashboard list: 52px rows, a 13.5px semibold header, hover in `app-hover`, selected rows in `app-selected`.

**Use** for every list page (Transactions, Customers, Shipments). Amount comes first, left-aligned in `app-ink` with tabular figures and no currency column. Rows open the detail drawer; the last column is a "…" row menu.

**Formats.** Money `Rp1.250.000`, dates `14 Okt 2026, 10:42`, phone `+62 812-3456-7890`.

**Don't** add row chevrons, or a Status column to lists that have no status. Wrap the table in `.fl-tblwrap` so it scrolls sideways on phones.
