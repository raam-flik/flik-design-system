# PartnerLogo

A payment or courier logo as a square tile: 24px with 6px corners (20px and 32px sizes), white behind the logo and a 1px `app-line` ring so white logos still have an edge.

**Use** wherever a bank, e-wallet, QRIS or courier is named: the payment method column, top-up and payment options, courier lists, rate results, tracking. Put the name next to it (`fl-pm`): the logo helps scanning, the words carry the meaning. Group several with `fl-plogos` (at most four, then "+3"). For a method with no logo file (cards, COD, a bank not yet in the set) use the `fl-plogo--icon` tile with the matching line icon. Files are in `assets/Logos/payment/` and `assets/Logos/courier/` (use the PNG; the courier SVGs only wrap a bitmap and are much heavier).

**Don't** draw a logo as coloured text ("gopay" on blue) or as initials, recolour or crop a logo, or put logos on a coloured tile. Never use a partner logo bigger than the FLIK logo on the same screen.
