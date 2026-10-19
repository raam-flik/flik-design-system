# EmptyState

The first-run view of a list page with no data yet: a soft `app-hover` panel with a large headline, one sentence, one primary button and a tile illustration, then two follow-up cards.

**Use** when a list is empty because the merchant has not started (Customers before the first sale). The headline says what will appear here; the sentence says how it fills itself; the button is the manual way in. The cards offer the other two routes (import, connect a product) and end in an underlined `fl-ulink`.

**Art.** Build it from `fl-tile`s: one `fl-tile--hub` in `primary` for the thing being collected, white tiles for the sources, fading out to the right. No photos, no gradients beyond the `primary-soft` wash.

**Don't** use it for "no results" after filtering; that is the plain table empty row.
