# FilterChip

A dashed pill that adds a filter to a list; once set it turns solid and shows the chosen value in `primary`.

**Use** in the filter row above tables, in this order: search, filters (each with its own icon), sort, Export, then the primary action.

**Don't** put more than five chips in a row; move the rest into a "More filters" chip.

**Lists that use `FilterBar`** (Monitoring, Transactions, Balances) no longer show chips: one Filter button replaces the row. FilterChip stays on the lists not moved yet (Shipments, Customers, Invoices) and on views without a table.
