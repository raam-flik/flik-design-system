# FAQ

A single-column accordion of questions; the plus tile turns 45° into a close mark when open.

**Use** near the end of product pages, before resources. The first question starts open. Max width 820px.

**Markup.** `.fl-faq > .fl-qa(.open) > button[aria-expanded] + .ans`. Toggle `open` and `aria-expanded` together on click.

**Don't** hide pricing or eligibility only inside the FAQ: state them on the page too.
