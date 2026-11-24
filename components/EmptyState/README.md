# EmptyState

The first-run view of a list page with no data yet: a soft `app-hover` panel with a large headline, one sentence, one primary button and a tile illustration, then two follow-up cards.

**Use** when a list is empty because the merchant has not started (Customers before the first sale). The headline says what will appear here; the sentence says how it fills itself; the button is the manual way in. The cards offer the other two routes (import, connect a product) and end in an underlined `fl-ulink`.

**Art.** Build it from `fl-tile`s: one `fl-tile--hub` in `primary` for the thing being collected, white tiles for the sources, fading out to the right. No photos, no gradients beyond the `primary-soft` wash.

**Don't** use it for "no results" after filtering; that is the empty table below.

## Empty table

Every table or list with no rows uses `fl-table-empty` (approved by Raam, 24 Nov 2026): a 48px `app-hover` tile with the search icon in `app-ink`, a 20px semibold title, one muted line, and at most one outline button (for example "Clear search and filters"). The block is left-aligned and centred in the table's space, with 72px above and below (less inside a side panel). On phones it stays in view while the table scrolls sideways.

- Write the words for the list it sits in; never a generic "No results".
- No data yet: the title names what isn't here ("No refunds yet", "No orders on hold"); the line says how it fills ("Refund a shopper from the payment: open it and choose Refund.").
- Nothing matches: "No {things} match" ("No shipments match"), then what to try, using the fields the search covers ("Try another AWB, or clear the search and filters."), plus the clear button when there is one.
