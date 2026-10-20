#!/usr/bin/env python3
"""Convert dashboard/index.html (plain CSS) into tailwind/dashboard/index.html (Tailwind v4 utilities).

How it works
- Every CSS rule becomes Tailwind utilities on the element it styles. The element is found by its
  "anchor" class (the last class in the selector). Hover, state classes (.on, .open, .sel …),
  parent selectors and media queries become variants: hover:, [&.on]:, [.grp.open_&]:, max-[960px]: …
- Values use the FLIK theme where they match a token (bg-primary, text-app-muted, shadow-app,
  rounded-control …); everything else becomes an exact arbitrary value.
- Element-only rules (body, h1, table, th, td …) go into @layer base.
- The original class names stay on the elements: the JavaScript uses them as hooks and state classes.

Run:  python3 scripts/convert_dashboard_to_tailwind.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "dashboard", "index.html")
OUT = os.path.join(ROOT, "tailwind", "dashboard", "index.html")
TW_BROWSER = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.13"

# Dashboard CSS variables -> FLIK theme names
VAR = {"ink": "app-ink", "text": "app-text", "muted": "app-muted", "faint": "app-faint", "line": "app-line",
       "line-2": "app-line-2", "hover": "app-hover", "search": "app-field", "primary": "primary",
       "primary-h": "primary-hover", "primary-soft": "primary-soft",
       "ok-bg": "badge-ok-bg", "ok-tx": "badge-ok-text", "ok-bd": "badge-ok-border",
       "gr-bg": "badge-neutral-bg", "gr-tx": "badge-neutral-text", "gr-bd": "badge-neutral-border",
       "warn-bg": "badge-warn-bg", "warn-tx": "badge-warn-text", "warn-bd": "badge-warn-border",
       "bad-bg": "badge-bad-bg", "bad-tx": "badge-bad-text", "bad-bd": "badge-bad-border",
       "pu-bg": "badge-info-bg", "pu-tx": "badge-info-text", "pu-bd": "badge-info-border"}
SHADOWVAR = {"sh": "app", "pop": "pop"}
HEX = {"#fff": "white", "#ffffff": "white", "#000": "black", "#df1b41": "bad", "#002d5d": "app-ink", "#6a4bff": "primary",
       "#f8f6ff": "app-selected", "#c4b8ff": "primary-disabled", "#b3093c": "app-danger-text", "#1ea672": "ok",
       "#f2efff": "primary-soft", "#eef3f9": "app-hover"}
RADIUS = {"4px": "btn", "5px": "badge", "6px": "control", "8px": "card", "12px": "lg", "999px": "pill", "50%": "full"}


def cssvar(v):
    """Rewrite var(--x) to the theme variable (for arbitrary values)."""
    def r(m):
        n = m.group(1)
        if n in VAR:
            return f"var(--color-{VAR[n]})"
        if n in SHADOWVAR:
            return f"var(--shadow-{SHADOWVAR[n]})"
        if n == "font":
            return "var(--font-sans)"
        return m.group(0)
    return re.sub(r"var\(--([\w-]+)\)", r, v)


def arb(v):
    return cssvar(v).replace(" ", "_")


def color_name(v):
    v = v.strip()
    m = re.fullmatch(r"var\(--([\w-]+)\)", v)
    if m and m.group(1) in VAR:
        return VAR[m.group(1)]
    if v.lower() in HEX:
        return HEX[v.lower()]
    if v in ("transparent", "currentColor", "inherit"):
        return {"currentColor": "current"}.get(v, v)
    return f"[{arb(v)}]"


def sp(v, neg_ok=True):
    """A length -> spacing suffix: 10px -> 2.5, 0 -> 0, auto -> auto, else [v]."""
    v = v.strip()
    if v in ("0", "0px"):
        return "0"
    if v == "auto":
        return "auto"
    if v == "100%":
        return "full"
    m = re.fullmatch(r"(-?)(\d+(?:\.\d+)?)px", v)
    if m:
        n = float(m.group(2)) / 4
        if n * 2 == int(n * 2):
            s = (str(int(n)) if n == int(n) else str(n))
            return ("-" if m.group(1) else "") + s
    return f"[{arb(v)}]"


def pref(prefix, val):
    """Join prefix with a spacing value, moving a leading minus in front."""
    if val.startswith("-"):
        return f"-{prefix}-{val[1:]}"
    return f"{prefix}-{val}"


def box(prefix, v):
    """padding/margin shorthand -> utilities."""
    parts = v.split()
    if len(parts) == 1:
        t = r = b = l = parts[0]
    elif len(parts) == 2:
        t = b = parts[0]; r = l = parts[1]
    elif len(parts) == 3:
        t = parts[0]; r = l = parts[1]; b = parts[2]
    else:
        t, r, b, l = parts
    T, R, B, L = (sp(x) for x in (t, r, b, l))
    if T == R == B == L:
        return [pref(prefix, T)]
    out = []
    if T == B:
        out.append(pref(prefix + "y", T))
    else:
        out += [pref(prefix + "t", T), pref(prefix + "b", B)]
    if R == L:
        out.append(pref(prefix + "x", R))
    else:
        out += [pref(prefix + "r", R), pref(prefix + "l", L)]
    return out


def size(prefix, v):
    v = v.strip()
    if v == "100%":
        return f"{prefix}-full"
    if v == "100vh":
        return f"{prefix}-screen"
    if v == "auto":
        return f"{prefix}-auto"
    return f"{prefix}-{sp(v)}" if prefix in ("w", "h", "min-w", "min-h") and not sp(v).startswith("[") else f"{prefix}-[{arb(v)}]"


WEIGHT = {"300": "light", "400": "normal", "500": "medium", "600": "semibold", "700": "bold"}
SIMPLE = {
    ("display", "flex"): "flex", ("display", "grid"): "grid", ("display", "block"): "block", ("display", "none"): "hidden",
    ("display", "inline-flex"): "inline-flex", ("display", "inline-block"): "inline-block", ("display", "inline"): "inline",
    ("flex-direction", "column"): "flex-col", ("flex-wrap", "wrap"): "flex-wrap", ("flex", "1"): "flex-1", ("flex", "none"): "flex-none",
    ("align-items", "center"): "items-center", ("align-items", "flex-start"): "items-start", ("align-items", "flex-end"): "items-end",
    ("align-items", "baseline"): "items-baseline", ("align-items", "start"): "items-start", ("align-items", "stretch"): "items-stretch",
    ("justify-content", "center"): "justify-center", ("justify-content", "space-between"): "justify-between",
    ("justify-content", "flex-end"): "justify-end", ("justify-content", "flex-start"): "justify-start",
    ("align-content", "start"): "content-start", ("align-content", "center"): "content-center", ("align-self", "start"): "self-start",
    ("justify-self", "center"): "justify-self-center", ("justify-self", "start"): "justify-self-start",
    ("position", "absolute"): "absolute", ("position", "relative"): "relative", ("position", "fixed"): "fixed",
    ("position", "sticky"): "sticky", ("position", "static"): "static",
    ("text-align", "left"): "text-left", ("text-align", "right"): "text-right", ("text-align", "center"): "text-center",
    ("white-space", "nowrap"): "whitespace-nowrap", ("white-space", "normal"): "whitespace-normal", ("white-space", "pre-wrap"): "whitespace-pre-wrap",
    ("cursor", "pointer"): "cursor-pointer", ("cursor", "default"): "cursor-default", ("cursor", "not-allowed"): "cursor-not-allowed",
    ("overflow", "hidden"): "overflow-hidden", ("overflow", "visible"): "overflow-visible", ("overflow-x", "auto"): "overflow-x-auto",
    ("overflow-y", "auto"): "overflow-y-auto", ("overflow", "auto"): "overflow-auto",
    ("pointer-events", "none"): "pointer-events-none", ("pointer-events", "auto"): "pointer-events-auto",
    ("font-variant-numeric", "tabular-nums"): "tabular-nums", ("user-select", "none"): "select-none",
    ("text-decoration", "underline"): "underline", ("text-decoration", "none"): "no-underline", ("text-transform", "uppercase"): "uppercase",
    ("font-style", "normal"): "not-italic", ("outline", "none"): "outline-none", ("outline", "0"): "outline-none",
    ("border", "0"): "border-0", ("border", "none"): "border-0", ("resize", "vertical"): "resize-y", ("object-fit", "contain"): "object-contain",
    ("word-break", "break-word"): "break-words", ("text-overflow", "ellipsis"): "text-ellipsis", ("flex", "1 1 auto"): "flex-auto",
    ("opacity", "0"): "opacity-0", ("opacity", "1"): "opacity-100", ("background", "none"): "bg-transparent",
    ("background", "transparent"): "bg-transparent", ("box-shadow", "none"): "shadow-none", ("transform", "none"): "transform-none",
    ("scrollbar-width", "none"): "[scrollbar-width:none]", ("margin-left", "auto"): "ml-auto", ("margin-top", "auto"): "mt-auto",
    ("grid-column", "1/-1"): "col-span-full", ("visibility", "hidden"): "invisible",
}


def border(side, v):
    """border(-side): 1px solid X -> border(-b) border-X (dashed too)."""
    parts = v.split()
    pre = "border" + (f"-{side}" if side else "")
    if v.strip() in ("0", "none"):
        return [f"{pre}-0"]
    out = []
    w = next((p for p in parts if re.fullmatch(r"[\d.]+px", p)), None)
    style = next((p for p in parts if p in ("solid", "dashed", "dotted")), None)
    col = next((p for p in parts if p not in (w, style)), None)
    if w:
        out.append(pre if w == "1px" else f"{pre}-[{w}]")
    if style and style != "solid":
        out.append(f"border-{style}")
    if col:
        c = color_name(col)
        out.append(f"border-{c}" if not side else f"border-{side}-{c}")
    return out


def decl(prop, val):
    """One declaration -> list of utilities (exact)."""
    prop = prop.strip().lower()
    val = val.strip()
    imp = val.endswith("!important")
    if imp:
        val = val[:-10].strip()
    out = None
    key = (prop, val)
    if key in SIMPLE:
        out = [SIMPLE[key]]
    elif prop == "gap":
        p = val.split()
        out = [f"gap-{sp(p[0])}"] if len(p) == 1 else [f"gap-y-{sp(p[0])}", f"gap-x-{sp(p[1])}"]
    elif prop in ("row-gap", "column-gap"):
        out = [f"gap-{'y' if prop == 'row-gap' else 'x'}-{sp(val)}"]
    elif prop == "padding":
        out = box("p", val)
    elif prop == "margin":
        out = box("m", val)
    elif re.fullmatch(r"(padding|margin)-(top|right|bottom|left)", prop):
        a, s = prop.split("-")
        out = [pref(a[0] + s[0], sp(val))]
    elif prop in ("width", "height", "min-width", "min-height"):
        p = {"width": "w", "height": "h", "min-width": "min-w", "min-height": "min-h"}[prop]
        out = [size(p, val)]
    elif prop in ("max-width", "max-height"):
        p = "max-w" if prop == "max-width" else "max-h"
        out = [f"{p}-full" if val == "100%" else f"{p}-[{arb(val)}]"]
    elif prop in ("top", "right", "bottom", "left", "inset"):
        out = [pref(prop, sp(val))]
    elif prop == "z-index":
        out = [f"z-{val}" if val in ("0", "10", "20", "30", "40", "50") else f"z-[{val}]"]
    elif prop == "border-radius":
        out = [f"rounded-{RADIUS[val]}" if val in RADIUS else f"rounded-[{arb(val)}]"]
    elif prop == "font-size":
        out = [f"text-[{val}]"]
    elif prop == "font-weight":
        out = [f"font-{WEIGHT.get(val, '[' + val + ']')}"]
    elif prop == "line-height":
        out = [f"leading-[{arb(val)}]"]
    elif prop == "letter-spacing":
        out = [f"tracking-[{arb(val)}]"]
    elif prop == "color":
        out = [f"text-{color_name(val)}"]
    elif prop in ("background", "background-color"):
        if re.fullmatch(r"(var\(--[\w-]+\)|#[0-9a-fA-F]{3,8})", val):
            out = [f"bg-{color_name(val)}"]
        else:
            out = [f"bg-[{arb(val)}]"] if prop == "background-color" else [f"[background:{arb(val)}]"]
    elif prop == "box-shadow":
        m = re.fullmatch(r"var\(--([\w-]+)\)", val)
        out = [f"shadow-{SHADOWVAR[m.group(1)]}"] if m and m.group(1) in SHADOWVAR else [f"shadow-[{arb(val)}]"]
    elif prop == "border":
        out = border("", val)
    elif prop in ("border-top", "border-right", "border-bottom", "border-left"):
        out = border(prop.split("-")[1][0], val)
    elif prop == "border-color":
        out = [f"border-{color_name(val)}"]
    elif prop == "border-style":
        out = [f"border-{val}"]
    elif prop == "font-family":
        out = ["font-sans"] if "var(--font)" in val else [f"font-[{arb(val)}]"]
    elif prop == "opacity":
        f = float(val)
        out = [f"opacity-{int(round(f * 100))}"]
    elif prop == "content":
        out = ["content-['']"] if val in ('""', "''") else [f"content-[{arb(val)}]"]
    elif prop == "flex":
        out = [f"[flex:{arb(val)}]"]
    elif prop == "grid-template-columns":
        m = re.fullmatch(r"repeat\((\d+),\s*1fr\)", val)
        out = [f"grid-cols-{m.group(1)}"] if m else (["grid-cols-1"] if val == "1fr" else [f"grid-cols-[{arb(val)}]"])
    else:
        out = [f"[{prop}:{arb(val)}]"]
    if imp:
        out = [u + "!" for u in out]
    return out


SHORT = {"&:hover": "hover:", "&:disabled": "disabled:", "&::before": "before:", "&::after": "after:", "&:last-child": "last:",
         "&:first-child": "first:", "&:focus": "focus:", "&:focus-within": "focus-within:", "&:focus-visible": "focus-visible:",
         "&::placeholder": "placeholder:", "&:active": "active:"}


def variant_for(selector):
    """Return (anchor_class, variant_prefix) for one selector, or (None, None) for element-only selectors."""
    sel = selector.strip()
    # tokens: compounds separated by combinators
    parts = re.split(r"(\s*[>+~]\s*|\s+)", sel)
    compounds = [p for p in parts[::2]]
    combs = [p for p in parts[1::2]]
    idx = None
    for i in range(len(compounds) - 1, -1, -1):
        if re.search(r"\.[A-Za-z][\w-]*", compounds[i]):
            idx = i
            break
    if idx is None:
        return None, None
    comp = compounds[idx]
    anchor = re.search(r"\.([A-Za-z][\w-]*)", comp).group(1)
    rest = comp.replace("." + anchor, "", 1)
    if rest.startswith(":not") or re.match(r"^[a-z]", rest):
        # element + class (e.g. th.sort) or :not() -> keep as & with the rest
        pass
    before = "".join(c + (combs[i] if i < len(combs) else "") for i, c in enumerate(compounds[:idx]))
    after = "".join((combs[i - 1] if i - 1 < len(combs) else "") + compounds[i] for i in range(idx + 1, len(compounds)))
    elem = ""
    m = re.match(r"^([a-z][a-z0-9]*)(.*)$", rest)
    if m:
        elem, rest = m.group(1), m.group(2)
    core = "&" + rest
    if elem:
        core = elem + core.replace("&", "&", 1)
        core = core.replace(elem + "&", "&") if False else core
    v = before + ("&" if not elem else "&") + rest + after
    if elem:
        v = before + "&" + rest + after  # tag on the anchor itself is implied (we only put classes on that tag)
    v = re.sub(r"\s*>\s*", ">", v)
    v = re.sub(r"\s*\+\s*", "+", v)
    v = re.sub(r"\s*~\s*", "~", v)
    v = re.sub(r"\s+", "_", v.strip())
    if v == "&":
        return anchor, ""
    if v in SHORT:
        return anchor, SHORT[v]
    return anchor, f"[{v}]:"


def parse_css(css):
    """Yield (media_prefix, selector_list, declarations) in source order."""
    i = 0
    out = []

    def rules(block, media):
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block):
            out.append((media, m.group(1).strip(), m.group(2)))
    pos = 0
    for m in re.finditer(r"@media\s*\(max-width:\s*(\d+)px\)\s*\{", css):
        pass
    # walk the css handling @media blocks
    depth = 0
    buf = ""
    j = 0
    while j < len(css):
        if css.startswith("@media", j):
            k = css.index("{", j)
            cond = css[j:k]
            mm = re.search(r"max-width:\s*(\d+)px", cond)
            media = f"max-[{mm.group(1)}px]:" if mm else ""
            # find matching brace
            d = 0
            e = k
            while True:
                if css[e] == "{":
                    d += 1
                elif css[e] == "}":
                    d -= 1
                    if d == 0:
                        break
                e += 1
            rules(buf, "")
            buf = ""
            rules(css[k + 1:e], media)
            j = e + 1
            continue
        buf += css[j]
        j += 1
    rules(buf, "")
    return out


def main():
    src = open(SRC).read()
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = parse_css(css)
    base = []
    # (anchor) -> ordered dict of (variant, prop) -> utilities
    per_anchor = {}
    order = 0
    for media, sel_list, body in rules:
        decls = [d.split(":", 1) for d in body.split(";") if ":" in d]
        for sel in [s.strip() for s in sel_list.split(",")]:
            if sel.startswith(":root"):
                continue
            anchor, var = variant_for(sel)
            if anchor is None:
                base.append((media, sel, body))
                continue
            slot = per_anchor.setdefault(anchor, {})
            for p, v in decls:
                order += 1
                slot[(media + var, p.strip().lower())] = (order, decl(p, v))
    # utilities per anchor, in source order
    util = {a: [(o, k[0], u) for k, (o, u) in d.items()] for a, d in per_anchor.items()}

    def merged(classes):
        """Merge utilities for a set of classes; later rules win per (variant, property)."""
        best = {}
        for c in classes:
            for (var, prop), (o, us) in per_anchor.get(c, {}).items():
                if (var, prop) not in best or best[(var, prop)][0] < o:
                    best[(var, prop)] = (o, var, us)
        items = sorted(best.values())
        res = []
        for o, var, us in items:
            for u in us:
                res.append(var + u)
        return res

    used = set()

    def convert_static(cls_text):
        toks = cls_text.split()
        names = [t for t in toks if re.fullmatch(r"[A-Za-z][\w-]*", t)]
        us = merged(names)
        for n in names:
            if n in per_anchor:
                used.add(n)
        return " ".join(toks + us) if us else cls_text

    body = src[src.index("</style>") + 8:]

    def fix_attr(m):
        q, val = m.group(1), m.group(2)
        # split into literal text and ${...} expressions
        out = []
        pos = 0
        for e in re.finditer(r"\$\{", val):
            pass
        segs = []
        i = 0
        while i < len(val):
            if val.startswith("${", i):
                d = 0
                j = i
                while j < len(val):
                    if val[j] == "{":
                        d += 1
                    elif val[j] == "}":
                        d -= 1
                        if d == 0:
                            break
                    j += 1
                segs.append(("expr", val[i:j + 1]))
                i = j + 1
            else:
                j = val.find("${", i)
                j = len(val) if j < 0 else j
                segs.append(("lit", val[i:j]))
                i = j
        static_names = []
        for kind, s in segs:
            if kind == "lit":
                static_names += [t for t in s.split() if re.fullmatch(r"[A-Za-z][\w-]*", t)]
        res = []
        for kind, s in segs:
            if kind == "lit":
                res.append(s)
            else:
                # class names added inside string literals of the expression get their own utilities
                def lit_in(mm):
                    class M:
                        pass
                    m2 = M()
                    m2.group = lambda k, _g=(mm.group(0).lstrip(), mm.group(2), mm.group(3)): _g[k]
                    return lit(m2)

                def lit(mm):
                    inner = mm.group(2)
                    names = [t for t in inner.split() if re.fullmatch(r"[A-Za-z][\w-]*", t)]
                    own = [n for n in names if n in per_anchor and n not in static_names]
                    if not own:
                        return mm.group(0)
                    us = merged(own)
                    used.update(own)
                    lead = " " if inner.startswith(" ") else ""
                    return mm.group(1) + lead + " ".join(inner.split() + us) + mm.group(1)
                # only literals the expression inserts as classes (ternary branches), never values it compares against
                res.append(re.sub(r"(?<=[?:{+(])(\s*)(')([^'$`]*)'", lambda mm: mm.group(1) + lit_in(mm), s))
        us = merged(static_names)
        for n in static_names:
            if n in per_anchor:
                used.add(n)
        joined = "".join(res).rstrip()
        if us:
            joined = joined + " " + " ".join(us)
        return f'class={q}{joined}{q}'

    body2 = re.sub(r'class=(["\'])((?:(?!\1).)*)\1', fix_attr, body, flags=re.S)
    # inline styles and JS strings that still use the old variables (--muted, --ink …)
    body2 = cssvar(body2)
    # JS that sets className directly
    body2 = body2.replace("className='delta '+(pc>=0?'up':'down')",
                          "className='delta '+(pc>=0?'up':'down')+' '+" + repr(" ".join(merged(["delta"]))))
    # a plain className='a b' literal keeps its names and gets their utilities
    body2 = re.sub(r"className='([\w -]+)'(?!\+)",
                   lambda mm: "className='" + " ".join([mm.group(1)] + merged(mm.group(1).split())) + "'", body2)
    # base layer for element selectors
    base.append(("", "small", "font-size:smaller"))  # Tailwind's preflight makes <small> 80%; keep the browser default
    base_css = []
    for media, sel, b in base:
        rule = f"{sel}{{{cssvar(b)}}}"
        if media:
            w = re.search(r"\d+", media).group(0)
            rule = f"@media (max-width:{w}px){{{rule}}}"
        base_css.append("  " + rule)
    head = src[:src.index("<style>")]
    head = head.replace("<title>FLIK Dashboard</title>", "<title>FLIK Dashboard (Tailwind)</title>")
    theme = open(os.path.join(ROOT, "tailwind", "theme.css")).read()
    style = (f'<!-- Tailwind v4 in the browser, for this prototype only. In a project, build with Tailwind and import ../theme.css. -->\n'
             f'<script src="{TW_BROWSER}"></script>\n<style type="text/tailwindcss">\n{theme}\n'
             "/* Element styles the dashboard relies on (tables, headings, page text). Everything else is utility classes in the markup. */\n"
             "@layer base {\n" + "\n".join(base_css) + "\n}\n</style>")
    out = head + style + body2
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(out)
    missing = sorted(set(per_anchor) - used)
    print(f"tailwind/dashboard/index.html written: {len(rules)} CSS rules converted, {len(base)} kept as base element styles")
    print("classes with styles that never appear in markup:", ", ".join(missing) or "none")


main()
