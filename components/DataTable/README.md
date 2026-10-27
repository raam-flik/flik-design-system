# DataTable

The dashboard list: 52px rows, a 13.5px semibold header, hover in `app-hover`, selected rows in `app-selected`.

**Use** for every list page (Transactions, Customers, Shipments). Amount comes first, left-aligned in `app-ink` with tabular figures and no currency column. Rows open the detail drawer; the last column is a "…" row menu.

**Columns, as in Stripe.** Each header is a button: hover shows a grip to drag the column somewhere else, and a click opens a `PopoverMenu` with Sort ascending, Sort descending, Pin column and Hide column. A sorted header shows its arrow; a pinned one shows a pin in `primary`, moves to the left and stays in view when the table scrolls sideways. The Edit columns button in the `FilterBar` lists every column with a grip, a checkbox to show or hide it and a pin, and ends with a full-width Reset. The setup is kept per list on that device. The key column (AWB, Amount, Claim ID) can't be hidden.

**Formats.** Money `Rp1.250.000`, dates `14 Oct 2026, 10:42`, phone `+62 812-3456-7890`, relative times without a space (`3h ago`).

**Don't** add row chevrons, or a Status column to lists that have no status. Wrap the table in `.fl-tblwrap` so it scrolls sideways on phones.
