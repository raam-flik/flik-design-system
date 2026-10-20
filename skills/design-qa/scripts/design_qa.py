#!/usr/bin/env python3
"""Static design QA for one FLIK HTML page or prototype.

Checks the file against the FLIK Design System tokens and rules and prints a
short Markdown report. Browser checks (real spacing, states, 375px) are done
afterwards with measure.js; see SKILL.md.

Usage: python3 design_qa.py <page.html> [--tokens path/to/tokens.json]
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_TOKENS = HERE.parents[2] / "tokens.json"  # design-system/tokens.json

# Spacing: the components use a 2px grid. Anything else is off-grid.
SPACING_OK = {0, 1, 2} | set(range(4, 129, 2)) | {160, 240, 320, 440, 460, 1180, 1266}
RADIUS_OK_EXTRA = {"0", "50%", "inherit", "999px", "100px", "2px", "3px"}  # 2-3px: tiny marks (checkbox, ticks)
WEIGHTS_OK = {300, 400, 500, 600}
FONTS_OK = ("inter", "jetbrains mono", "ui-monospace", "monospace", "sans-serif", "system-ui",
            "-apple-system", "blinkmacsystemfont", "segoe ui", "roboto", "helvetica", "arial", "inherit", "sfmono-regular", "menlo")
INTERACTIVE = re.compile(r"\.((?:btn|abtn|chip|tab|ni|seg|opt|svc|ib|iconbtn|link|choice|dots-b|qa|es-link|mi|rdo|cb)[\w-]*)")


def load_tokens(path):
    t = json.loads(Path(path).read_text())
    colours = {}
    for theme in [t["color"]["tokens"]] + [x.get("tokens", []) for x in t["color"].get("themes", []) if isinstance(x, dict)]:
        for c in theme if isinstance(theme, list) else []:
            v = str(c.get("value", "")).lower()
            if v.startswith("#"):
                colours.setdefault(norm_hex(v), c["name"])
    radii = {r["value"] for r in t["radius"]["tokens"]}
    sizes, weights = set(), set(WEIGHTS_OK)
    for g in t["type"]["groups"]:
        for s in g.get("styles", []):
            sizes.add(str(s.get("fontSize")))
            weights.add(int(s.get("fontWeight", 400)))
    return colours, radii, sizes, weights


def norm_hex(h):
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(ch * 2 for ch in h[1:])
    return h[:7]


def line_of(text, idx, cache={}):
    key = id(text)
    if key not in cache:
        cache[key] = [m.start() for m in re.finditer("\n", text)]
    import bisect
    return bisect.bisect_left(cache[key], idx) + 1


def skip_zone(text):
    """Ranges to ignore: inline logos and images (third-party marks keep their colours)."""
    zones = []
    for m in re.finditer(r"data:image[^\"')]+|<svg[^>]*class=\"[^\"]*logo[\s\S]*?</svg>|LOGO\s*=\s*`[\s\S]*?`|cLogo[\s\S]{0,40}?=>[\s\S]{0,4000}?\n\S", text):
        zones.append((m.start(), m.end()))
    return zones


def inside(zones, i):
    return any(a <= i < b for a, b in zones)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    page = Path(args[0])
    tok = Path(args[args.index("--tokens") + 1]) if "--tokens" in args else DEFAULT_TOKENS
    colours, radii, sizes, weights = load_tokens(tok)
    # Values the approved components already use count as part of the system.
    bundle = tok.parent / "components" / "bundle.css"
    if bundle.exists():
        b = bundle.read_text()
        sizes |= set(re.findall(r"font-size:\s*([\d.]+px)", b))
        radii |= {v for v in re.findall(r"border-radius:\s*([\d.]+px|[\d.]+%)", b)}
        weights |= {int(w) for w in re.findall(r"font-weight:\s*(\d{3})", b)}
    text = page.read_text()
    zones = skip_zone(text)
    out = defaultdict(list)  # severity -> [(rule, detail)]

    def add(sev, rule, items):
        if items:
            out[sev].append((rule, items))

    def where(occ):
        return ", ".join(f"L{l}" for l in sorted(set(occ))[:4]) + (" …" if len(set(occ)) > 4 else "")

    # 1. Colours
    bad_hex, typed_hex = defaultdict(list), defaultdict(list)
    for m in re.finditer(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b(?![0-9a-fA-F])", text):
        i = m.start()
        if inside(zones, i):
            continue
        before = text[max(0, i - 40):i]
        if re.search(r"(href|id|data-[\w-]+)=[\"']?$|location\.hash|url\(#", before):
            continue
        h = norm_hex(m.group())
        is_var_def = re.search(r"--[\w-]+\s*:\s*$", before) is not None
        if h not in colours:
            bad_hex[h].append(line_of(text, i))
        elif not is_var_def:
            typed_hex[h].append(line_of(text, i))
    add("FAIL", "Colour not in the design system",
        [f"`{h}` ×{len(v)} ({where(v)})" for h, v in sorted(bad_hex.items(), key=lambda x: -len(x[1]))])
    add("WARN", "Typed hex instead of var(--token)",
        [f"`{h}` = `--{colours[h]}` ×{len(v)} ({where(v)})" for h, v in sorted(typed_hex.items(), key=lambda x: -len(x[1]))])
    grads = [line_of(text, m.start()) for m in re.finditer(r"(linear|radial|conic)-gradient\(", text) if not inside(zones, m.start())]
    add("WARN", "Gradient (only the brand ribbon may use one)", [f"×{len(grads)} ({where(grads)})"] if grads else [])

    # 2. Declarations
    decl = re.compile(r"(?<![\w-])(margin(?:-\w+)?|padding(?:-\w+)?|gap|row-gap|column-gap|border-radius|font-size|font-weight|font-family|font)\s*:\s*([^;}\"'`]+)")
    spacing, radius, fsize, fweight, ffam = (defaultdict(list) for _ in range(5))
    all_space = Counter()
    for m in decl.finditer(text):
        prop, val, ln = m.group(1), m.group(2).strip(), line_of(text, m.start())
        if "${" in val or "var(" in val and prop != "font-family":
            pass
        if prop.startswith(("margin", "padding")) or prop.endswith("gap"):
            for px in re.findall(r"(-?\d*\.?\d+)px", val):
                n = abs(float(px))
                all_space[n] += 1
                if n not in SPACING_OK:
                    spacing[f"{px}px"].append(ln)
        elif prop == "border-radius":
            for part in val.split():
                if part.startswith("var(") or part in radii or part in RADIUS_OK_EXTRA:
                    continue
                radius[part].append(ln)
        elif prop == "font-size":
            if not val.startswith(("var(", "inherit", "100%", "1em")) and val not in sizes:
                fsize[val].append(ln)
        elif prop == "font-weight":
            if val.isdigit() and int(val) not in weights:
                fweight[val].append(ln)
        elif prop == "font-family":
            fams = [f.strip(" \"'").lower() for f in val.split(",")]
            for f in fams:
                if f and not f.startswith("var(") and not f.startswith(FONTS_OK):
                    ffam[f].append(ln)
    add("WARN", "Spacing off the 2px grid", [f"`{k}` ×{len(v)} ({where(v)})" for k, v in sorted(spacing.items(), key=lambda x: -len(x[1]))])
    add("WARN", "Radius not used anywhere in the design system", [f"`{k}` ×{len(v)} ({where(v)})" for k, v in sorted(radius.items(), key=lambda x: -len(x[1]))])
    add("WARN", "Font size not used anywhere in the design system", [f"`{k}` ×{len(v)} ({where(v)})" for k, v in sorted(fsize.items(), key=lambda x: -len(x[1]))])
    add("WARN", "Font weight not used by the system", [f"`{k}` ×{len(v)} ({where(v)})" for k, v in fweight.items()])
    add("FAIL", "Typeface other than Inter / JetBrains Mono", [f"`{k}` ({where(v)})" for k, v in ffam.items()])

    # 3. Interaction states in CSS
    css = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", text))
    base, hover, focus, disabled, active = set(), set(), set(), set(), set()
    for sel in re.findall(r"([^{}]+)\{", css):
        for s in sel.split(","):
            for c in INTERACTIVE.findall(s):
                root = c.split(":")[0]
                if ":hover" in s: hover.add(root)
                elif ":focus" in s: focus.add(root)
                elif ":disabled" in s or "[disabled]" in s or ".dis" in s: disabled.add(root)
                elif ":active" in s: active.add(root)
                else: base.add(root)
    used = lambda c: re.search(r"class=\"[^\"]*\b" + re.escape(c) + r"\b", text) or re.search(r"class=\\?['\"`][^'\"`]*\b" + re.escape(c) + r"\b", text)
    roots = {c for c in base if used(c) and not re.search(r"(-[a-z]$|--|-(ic|l|n|d|p|v|t|ct|lbl|val)$)", c)}
    containers = re.compile(r"(s|grid|wrap|row|list|mixed|group)$")
    def has_hover(c):
        return any(h == c or h.startswith(c + "-") or c.startswith(h + "-") for h in hover)
    add("WARN", "Interactive class with no :hover rule", sorted(c for c in roots if not has_hover(c) and not containers.search(c)))
    no_focus = "focus-visible" not in css
    add("FAIL" if no_focus else "INFO", "Keyboard focus",
        ["No :focus-visible rule anywhere"] if no_focus else [f"{len(focus)} classes have a focus rule; check the rest inherit a global one"])
    add("WARN", "Disabled state", [] if disabled or ":disabled" in css else ["No :disabled / [disabled] style found"])

    # 4. Content states (presence only; confirm each screen in the browser)
    probes = {
        "Empty (list with no data)": r"No [a-z]+ yet|class=\"[^\"]*\bempty|EmptyState|es-hero",
        "No results (search/filter)": r"No (results|matches)|Nothing matches|Clear filters",
        "Loading": r"[Ll]oading|skeleton|spinner|aria-busy",
        "Error / retry": r"Couldn.t|Try again|went wrong|aria-invalid|\bfld-err|\berror\b",
        "Field validation message": r"Enter (a|an|the)|is required|Must be|aria-invalid",
        "Success confirmation": r"toast\(|SuccessBanner|sx-ok|fl-success",
        "Disabled primary until valid": r"disabled",
        "Long text truncation": r"text-overflow:\s*ellipsis|line-clamp",
        "Pagination / many rows": r"[Pp]revious|[Nn]ext page|pagination|of \$\{",
    }
    rows = []
    for name, rx in probes.items():
        n = len(re.findall(rx, text))
        rows.append(f"{'found' if n else 'MISSING'}: {name}" + (f" (×{n})" if n else ""))
    add("INFO", "Content states found in the file (verify per screen)", rows)
    missing = [r.split(": ", 1)[1] for r in rows if r.startswith("MISSING")]
    add("WARN", "States with no trace in the file", missing)

    # 5. Accessibility basics
    imgs = [line_of(text, m.start()) for m in re.finditer(r"<img(?![^>]*\balt=)[^>]*>", text)]
    add("WARN", "<img> without alt", [where(imgs)] if imgs else [])
    iconbtn = [line_of(text, m.start()) for m in re.finditer(
        r"<button(?![^>]*aria-label)[^>]*>\s*(?:\$\{ic\([^)]*\)\}|<span data-ic=\"[^\"]*\"></span>|<svg[\s\S]{0,400}?</svg>)\s*</button>", text)]
    add("WARN", "Icon-only button without aria-label", [f"×{len(iconbtn)} ({where(iconbtn)})"] if iconbtn else [])
    inputs = [line_of(text, m.start()) for m in re.finditer(r"<(input|select|textarea)(?![^>]*(aria-label|type=\"hidden\"|id=))[^>]*>", text)]
    add("WARN", "Field with no label (no id for <label for>, no aria-label)", [f"×{len(inputs)} ({where(inputs)})"] if inputs else [])

    # 6. Copy and formats
    copy = {
        "Money with a space (`Rp 1.000`, use `Rp1.000`)": r"Rp\s\d",
        "Slash dates (use `14 Oct 2026`)": r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        "Indonesian month in English UI (Okt, Agu, Mei, Des)": r"\b\d{1,2} (Okt|Agu|Mei|Des) \d{4}",
        "Filler words (successfully, please, simply, seamless)": r"\b([Ss]uccessfully|[Pp]lease|[Ss]imply|[Ss]eamless)\b",
        "Exclamation mark in UI text": r">[^<>{}$`]*[A-Za-z]![^=<>]*<",
        "Click here": r"[Cc]lick here",
        "Lorem ipsum / TODO left in": r"[Ll]orem ipsum|TODO|FIXME|XXX",
    }
    for name, rx in copy.items():
        hits = [line_of(text, m.start()) for m in re.finditer(rx, text)]
        add("WARN", name, [f"×{len(hits)} ({where(hits)})"] if hits else [])

    # 7. Things the design system says never to add back
    never = {"Breadcrumbs": r"breadcrumb", "Row chevrons": r"<td[^>]*>\s*\$\{ic\('chev", "Helper subtitle under the page title": r"<h1[^>]*>[^<]*</h1>\s*<p"}
    for name, rx in never.items():
        hits = [line_of(text, m.start()) for m in re.finditer(rx, text, re.I)]
        add("FAIL", f"Removed pattern is back: {name}", [where(hits)] if hits else [])

    # Report
    print(f"# Design QA: {page.name}\n")
    total = {s: sum(len(i) for _, i in out[s]) for s in ("FAIL", "WARN")}
    print(f"**{total['FAIL']} fail · {total['WARN']} warn** (static checks; run the browser pass next)\n")
    for sev in ("FAIL", "WARN", "INFO"):
        for rule, items in out[sev]:
            print(f"- **{sev}** {rule}")
            for it in items[:12]:
                print(f"  - {it}")
            if len(items) > 12:
                print(f"  - … {len(items) - 12} more")
    top = ", ".join(f"{k:g}px×{v}" for k, v in all_space.most_common(12))
    print(f"\nSpacing in use (most common): {top}")


if __name__ == "__main__":
    main()
