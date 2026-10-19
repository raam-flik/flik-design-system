# CollapsibleCard

One record in a multi-record form (Shipment 1, Shipment 2 …): a header with the name, a green tick once complete, a one-line summary when closed, and the fields inside when open.

**Use** in Create shipment, with Add shipment and Reset below the cards. Adding a card closes the others. Fields use `FormField` with affixes: `+62` before phone numbers, `Rp` before amounts, `cm` / `kg` after sizes.

**Don't** validate with red text; the tick shows when a card is ready and the footer's Continue enables when all are.
