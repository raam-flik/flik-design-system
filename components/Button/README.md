# Button

The marketing call-to-action: 40px tall, 4px corners, 15px medium label.

**Use** one `fl-btn--primary` per view for the main action (Contact sales, Apply now, Start shipping free) and `fl-btn--secondary` beside it for the second choice. On the `dark` band use `fl-btn--on-dark` for the second button.

**Markup.** `<button class="fl-btn fl-btn--primary">Label <span class="fl-arrow">…</span></button>`. Add the `fl-arrow` SVG (two paths, `l` and `t`) after links that go somewhere: on hover the chevron grows a stem and slides 3px right.

**Behaviour.** Hover lifts the button 1px and gives the primary a violet shadow; press sinks it (scale .98). Disabled primary uses `primary-disabled`. Keyboard focus shows `focus-ring`.

**Don't** put two primary buttons side by side, use orange or gradients on buttons, or shorten the 40px height (stack full width on phones instead: 46px tall).
