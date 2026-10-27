# FilterBar

The toolbar above a list: a search field, one **Filter** button and an **Edit columns** button, with Export and the primary action at the end of the row. Modelled on Stripe.

**Use** on every list page (Monitoring, Transactions, Balances). The Filter button opens a `PopoverMenu` listing each filter with its current value; picking one opens its options: radios for the date (Today, This week, This month, This year, Custom) and checkboxes with Clear and Apply for the rest. When filters are on, the button turns `primary` on `primary-soft` and reads "1 filter" or "2 filters", and its menu ends with a full-width Clear all. Lists open with no filters. Search takes several AWBs at once (one per line, or separated by spaces or commas) and says how many it found. Edit columns opens the column settings of the `DataTable` below it.

**Don't** show active filters as a row of pills under the toolbar, or start a list with a default filter switched on. Hide the Filter button on a list that has nothing to filter, and keep the whole toolbar on one row at 1440px.
