# StatGrid

A ruled row of four big numbers with short captions, in the style of stripe.com/billing.

**Use** once per page, right after the hero, for the claims a buyer remembers. Numbers in the `stat` style (48px light), captions in `stat-text`.

**Layout.** The grid's top and bottom rules run out to the two guide lines: on a page with guides, give the section `container-type:inline-size` and pull the grid out by `calc(max(0px,50cqw - 590px) + 32px - max(16px,50cqw - 633px))` on each side. Two columns below 1080px.

**Don't** invent figures. Every number must come from the product reference (40% off, 3% COD fee, 99% creation success, 30-second checkout).
