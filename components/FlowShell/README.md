# FlowShell

The full-screen frame for creating something: a 60px top bar with close (×), the flow title and its actions or steps, a scrolling body, and (for stepped flows) a fixed 64px footer.

**Use** for Create invoice (editor: form left, `DocumentPreview` right, Hide preview + Review invoice in the top bar) and Create shipment (put a `Stepper` in the top bar, Back / Continue in the footer, a `SummaryPanel` beside the form). It covers the whole viewport and has its own URL (`#invoices/create`).

**Behaviour.** The primary stays disabled until the step is complete; never show error text for incomplete fields. × closes the flow; a filled invoice is kept as a Draft. On phones the editor shows the form and a "Show preview" button switches to the preview.

**Don't** open a create flow in a drawer or a small modal; modals are for one-question tasks inside it (an address, a confirmation).
