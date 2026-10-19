#!/usr/bin/env python3
"""Build the Tailwind v4 version of the FLIK Design System.

- tailwind/theme.css      the @theme block, generated from tokens.json
- tailwind/index.html     the gallery of every component in tailwind/components/*.html

Run after changing tokens.json or a component:  python3 scripts/build_tailwind.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TW = os.path.join(ROOT, "tailwind")
TW_BROWSER = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.13"
tokens = json.load(open(os.path.join(ROOT, "tokens.json")))

# Token name -> Tailwind theme variable, where the plain name would clash or read badly
SHADOW = {"shadow-sm": "sm", "shadow-lg": "lg", "shadow-hover": "hover", "app-shadow": "app", "app-pop": "pop", "focus-ring": "focus"}
RADIUS = {"radius-btn": "btn", "radius-badge": "badge", "radius-control": "control", "radius-card": "card", "radius-lg": "lg", "radius-pill": "pill"}
SPACING = {"gutter": "gutter", "gutter-mobile": "gutter-mobile", "section-y": "section", "section-y-sm": "section-sm",
           "card-pad": "card", "grid-gap": "grid", "app-sidebar": "sidebar", "app-content-x": "content", "app-row": "row"}
CONTAINER = {"container": "site", "guide-gap": "guides"}
# "body" is also a colour token, so the text size is text-paragraph (text-body stays the colour)
TEXT = {"body": "paragraph"}


def theme_css():
    out = ["/* FLIK Design System for Tailwind CSS v4. Generated from tokens.json by scripts/build_tailwind.py; do not edit by hand.",
           "   How to use it: see tailwind/README.md (import Tailwind first, then this file).",
           "   Tailwind's default colour palette is switched off: only FLIK colours exist (bg-primary, text-ink, border-app-line ...). */",
           "", "@theme {", "  /* Colours: only these. */", "  --color-*: initial;", "  --color-white: #ffffff;", "  --color-black: #000000;"]
    for t in tokens["color"]["tokens"]:
        v = t["value"] if isinstance(t["value"], str) else next(iter(t["value"].values()))
        out.append(f"  --color-{t['name']}: {v};")
    out += ["", "  /* Type */"]
    fam = tokens["type"]["families"]
    out.append(f"  --font-sans: {fam['sans']};")
    out.append(f"  --font-mono: {fam['mono']};")
    for g in tokens["type"]["groups"]:
        out.append(f"  /* {g['name']} text styles: text-<name> sets size, line height, weight and tracking */")
        for s in g["styles"]:
            n = TEXT.get(s["name"], s["name"])
            out.append(f"  --text-{n}: {s['fontSize']};")
            lh = s["lineHeight"]
            out.append(f"  --text-{n}--line-height: {lh};")
            out.append(f"  --text-{n}--font-weight: {s['fontWeight']};")
            if "letterSpacing" in s:
                out.append(f"  --text-{n}--letter-spacing: {s['letterSpacing']};")
    out += ["", "  /* Corners: rounded-btn, rounded-badge, rounded-control, rounded-card, rounded-lg, rounded-pill */"]
    for t in tokens["radius"]["tokens"]:
        out.append(f"  --radius-{RADIUS.get(t['name'], t['name'])}: {t['value']};")
    out += ["", "  /* Shadows: shadow-sm, shadow-lg, shadow-hover (website); shadow-app, shadow-pop (dashboard); shadow-focus */"]
    for t in tokens["shadow"]["tokens"]:
        out.append(f"  --shadow-{SHADOW.get(t['name'], t['name'])}: {t['value']};")
    out += ["", "  /* Named spacing (p-gutter, py-section, w-sidebar, h-row ...) and widths (max-w-site) */"]
    for t in tokens["spacing"]["tokens"]:
        if t["name"] in CONTAINER:
            out.append(f"  --container-{CONTAINER[t['name']]}: {t['value']};")
        else:
            out.append(f"  --spacing-{SPACING.get(t['name'], t['name'])}: {t['value']};")
    out += ["}", "",
            "@layer base {",
            "  body { font-family: var(--font-sans); color: var(--color-ink); background: var(--color-surface); -webkit-font-smoothing: antialiased; }",
            "}", ""]
    return "\n".join(out)


css = theme_css()
os.makedirs(TW, exist_ok=True)
open(os.path.join(TW, "theme.css"), "w").write(css)

# ---------- gallery ----------
GROUPS = [("Website", "website"), ("Dashboard", "dashboard"), ("Dashboard flows", "flows")]
comp_dir = os.path.join(TW, "components")
items = {k: [] for _, k in GROUPS}
for f in sorted(os.listdir(comp_dir)):
    if not f.endswith(".html"):
        continue
    src = open(os.path.join(comp_dir, f)).read()
    m = re.match(r"<!--\s*group:(\w+)\s*\|\s*(.*?)\s*-->\n", src)
    group, desc = (m.group(1), m.group(2)) if m else ("dashboard", "")
    body = src[m.end():] if m else src
    items.setdefault(group, []).append((f[:-5], desc, body.strip()))

cards = []
nav = []
for title, key in GROUPS:
    if not items.get(key):
        continue
    nav.append(f'<a href="#{key}" class="rounded-pill px-3 py-1.5 text-control text-app-text shadow-app hover:text-primary">{title}</a>')
    cards.append(f'<h2 id="{key}" class="mt-14 scroll-mt-20 text-section-title text-app-ink">{title}</h2>')
    for name, desc, body in items[key]:
        words = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
        cards.append(
            f'<article class="mt-4 overflow-hidden rounded-lg bg-white shadow-app">'
            f'<header class="flex items-start justify-between gap-4 px-5 pt-4 pb-3"><div><h3 class="text-[16px] font-semibold text-app-ink">{words}</h3>'
            f'<p class="mt-0.5 text-[14px] text-app-muted">{html.escape(desc)}</p></div>'
            f'<a href="components/{name}.html" class="shrink-0 text-control text-primary hover:text-primary-hover">View code</a></header>'
            f'<div class="border-y border-app-line bg-app-hover p-6">{body}</div>'
            f'<details class="group"><summary class="cursor-pointer list-none px-5 py-3 text-control text-app-muted hover:text-app-ink">Show markup</summary>'
            f'<pre class="max-h-96 overflow-auto bg-dark px-5 py-4 font-mono text-[12.5px] leading-relaxed text-code-text">{html.escape(body)}</pre></details></article>')

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FLIK Design System for Tailwind</title>
<link rel="icon" href="../assets/Logos/flik-mark.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<!-- Tailwind v4 in the browser, for this gallery only. In a project, build with Tailwind and @import "theme.css". -->
<script src="{TW_BROWSER}"></script>
<style type="text/tailwindcss">
{css}
</style>
</head>
<body class="bg-white">
<header class="sticky top-0 z-20 border-b border-app-line bg-white/90 backdrop-blur">
  <div class="mx-auto flex h-15 max-w-site items-center gap-4 px-6">
    <img src="../assets/Logos/flik-wordmark.svg" alt="FLIK" class="h-6">
    <span class="font-semibold text-app-ink">Design System · Tailwind</span>
    <nav class="ml-auto flex gap-2 overflow-x-auto">{"".join(nav)}</nav>
  </div>
</header>
<main class="mx-auto max-w-site px-6 pb-24">
  <section class="pt-14">
    <h1 class="text-display text-ink max-md:text-[38px]">FLIK for Tailwind CSS v4</h1>
    <p class="mt-4 max-w-[640px] text-lead text-muted">Every FLIK component as Tailwind utility classes, on a theme that only contains FLIK colours, type, corners and shadows. Copy the markup; add <code class="rounded bg-app-field px-1.5 py-0.5 font-mono text-[13px] text-app-ink">theme.css</code> to your project.</p>
    <div class="mt-6 rounded-lg bg-primary-soft px-5 py-4 text-[15px] text-app-ink"><b class="text-primary">Same two rules.</b> Reuse these components before making new ones, and use only FLIK colours. The theme switches Tailwind's default palette off, so <code class="font-mono text-[13px]">bg-blue-500</code> simply doesn't exist here.</div>
  </section>
  {"".join(cards)}
</main>
</body>
</html>
'''
open(os.path.join(TW, "index.html"), "w").write(page)
print(f"tailwind/theme.css and tailwind/index.html written ({sum(len(v) for v in items.values())} components)")
