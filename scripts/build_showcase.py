#!/usr/bin/env python3
"""Build index.html: a visual, non-technical overview of the FLIK Design System.

Reads tokens.json, README.md and components/*/ (preview.html + README.md) and writes
index.html at the repo root. Run from anywhere:  python3 scripts/build_showcase.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
esc = html.escape


def md_inline(s):
    """The little Markdown the guides use: **bold**, `code`, [text](url)."""
    s = esc(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


tokens = json.load(open(P("tokens.json")))
colors = {t["name"]: t for t in tokens["color"]["tokens"]}
readme = open(P("README.md")).read()


def section(title):
    m = re.search(r"^## " + re.escape(title) + r"\n(.*?)(?=^## |\Z)", readme, re.S | re.M)
    return m.group(1).strip() if m else ""


# ---------- Colours ----------
PALETTE = [
    ("Navy", "#002D5D", "Headlines, the dashboard's text and the dark sections."),
    ("Violet", "#6A4BFF", "The one action colour: buttons, links, selected tabs."),
    ("Cyan", "#00E5FF", "Brand ribbon and glows. Never for text."),
    ("Magenta", "#FF2DB8", "Brand ribbon and glows. Never for text."),
    ("Orange", "#FF7A2E", "Leads the brand ribbon. Never for text."),
]
GROUPS = [
    ("Actions", "What people click.", lambda n: n.startswith("primary") or n == "on-primary"),
    ("Brand ribbon", "Only for the hero wave and soft glows behind mockups.", lambda n: n.startswith("ribbon")),
    ("Logo colours", "Belong to the FLIK logo only.", lambda n: n.startswith("flik-")),
    ("Website text and backgrounds", "The marketing site.", lambda n: n in ("ink", "body", "muted", "faint", "surface", "surface-alt", "line", "line-soft", "guide", "line-strong", "stat-text", "neutral-soft")),
    ("Dark section", "The one dark band a page may have (Developers, COD).", lambda n: n.startswith("dark") or n.startswith("on-dark") or n == "code-text"),
    ("Status (website)", "Success, warning and error on the website.", lambda n: n.split("-")[0] in ("ok", "warn", "bad")),
    ("Dashboard", "Text, lines and backgrounds inside the merchant dashboard.", lambda n: n.startswith("app-")),
    ("Status badges (dashboard)", "Paid, Pending, Failed and so on. Always with the word, never colour alone.", lambda n: n.startswith("badge-")),
]


def luminance(hexv):
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def swatch(name, value, usage, big=False):
    ink = "#fff" if luminance(value) < 0.4 else "#002D5D"
    cls = "sw big" if big else "sw"
    return (f'<button class="{cls}" data-copy="{esc(value.upper())}" title="Copy {esc(value.upper())}">'
            f'<span class="chip" style="background:{value};color:{ink}">{esc(value.upper())}</span>'
            f'<span class="nm">{esc(name)}</span><span class="us">{md_inline(usage)}</span></button>')


used = set()
color_html = '<div class="pal">' + "".join(swatch(n, v, u, True) for n, v, u in PALETTE) + "</div>"
for title, desc, test in GROUPS:
    items = [t for t in tokens["color"]["tokens"] if test(t["name"]) and t["name"] not in used]
    used.update(t["name"] for t in items)
    if not items:
        continue
    color_html += f'<h3>{esc(title)}</h3><p class="gd">{esc(desc)}</p><div class="sws">'
    color_html += "".join(swatch(t["name"], t["value"], t.get("usage", "")) for t in items) + "</div>"

# ---------- Typography ----------
type_html = ""
for g in tokens["type"]["groups"]:
    gname = {"Marketing": "Website", "Product": "Dashboard"}.get(g["name"], g["name"])
    type_html += f"<h3>{esc(gname)}</h3><div class='types'>"
    for s in g["styles"]:
        fam = s.get("family", g["family"])
        style = (f"font-family:var(--font-{fam});font-size:{s['fontSize']};line-height:{s['lineHeight']};"
                 f"font-weight:{s['fontWeight']};letter-spacing:{s.get('letterSpacing', 'normal')}")
        w = {300: "Light", 400: "Regular", 500: "Medium", 600: "Semibold"}.get(s["fontWeight"], s["fontWeight"])
        type_html += (f'<div class="ty"><div class="meta"><b>{esc(s["name"])}</b><span>{esc(s["fontSize"])} · {w}</span>'
                      f'<span class="us">{md_inline(s.get("usage", ""))}</span></div>'
                      f'<div class="sample" style="{style}">{esc(s.get("sample", "FLIK"))}</div></div>')
    type_html += "</div>"

# ---------- Shape, depth, spacing ----------
shape_html = "<h3>Corners</h3><div class='shapes'>"
for t in tokens["radius"]["tokens"]:
    shape_html += (f'<div class="shp"><span class="box" style="border-radius:{t["value"]}"></span>'
                   f'<b>{esc(t["name"])}</b><span>{esc(t["value"])}</span><span class="us">{md_inline(t.get("usage", ""))}</span></div>')
shape_html += "</div><h3>Shadows</h3><div class='shapes'>"
for t in tokens["shadow"]["tokens"]:
    shape_html += (f'<div class="shp"><span class="box sh" style="box-shadow:{t["value"]}"></span>'
                   f'<b>{esc(t["name"])}</b><span class="us">{md_inline(t.get("usage", ""))}</span></div>')
shape_html += "</div><h3>Spacing</h3><div class='spaces'>"
for t in tokens["spacing"]["tokens"]:
    v = t["value"]
    px = float(re.sub(r"[^\d.]", "", v) or 0)
    bar = min(px, 320)
    shape_html += (f'<div class="sp"><b>{esc(t["name"])}</b><span class="v">{esc(v)}</span>'
                   f'<span class="bar" style="width:{bar}px"></span><span class="us">{md_inline(t.get("usage", ""))}</span></div>')
shape_html += "</div>"

# ---------- Components ----------
GROUP_INFO = {
    "Marketing": ("Website components", "Used on flik.co.id: buttons, links, headings, cards."),
    "Product": ("Dashboard components", "The building blocks of every dashboard page."),
    "Product flows": ("Dashboard flows", "Bigger pieces from the Customers, Invoices and Shipments pages."),
}
comps = {}
for name in sorted(os.listdir(P("components"))):
    d = P("components", name)
    if not os.path.isdir(d) or name == "Cover":
        continue
    prev = open(os.path.join(d, "preview.html")).read()
    group = (re.search(r'group="([^"]+)"', prev.splitlines()[0]) or [None, "Other"])[1]
    body = re.search(r"<body>(.*)</body>", prev, re.S).group(1).strip()
    guide = open(os.path.join(d, "README.md")).read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", re.sub(r"^# .*\n", "", guide)) if p.strip()]
    summary = paras[0] if paras else ""
    use = next((p for p in paras if p.startswith("**Use")), "")
    dont = next((p for p in paras if p.startswith("**Don't")), "")
    comps.setdefault(group, []).append((name, body, summary, use, dont))

comp_nav, comp_html = [], ""
for group in ["Marketing", "Product", "Product flows"] + [g for g in comps if g not in GROUP_INFO]:
    if group not in comps:
        continue
    title, desc = GROUP_INFO.get(group, (group, ""))
    gid = re.sub(r"\W+", "-", title.lower()).strip("-")
    comp_nav.append((gid, title))
    comp_html += f'<h3 id="{gid}">{esc(title)}</h3><p class="gd">{esc(desc)}</p>'
    for name, body, summary, use, dont in comps[group]:
        words = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
        comp_html += (f'<article class="cp" id="c-{name}"><header><h4>{esc(words)}</h4><p>{md_inline(summary)}</p></header>'
                      f'<div class="stage">{body}</div>'
                      f'<div class="rules">{"<p>" + md_inline(use) + "</p>" if use else ""}{"<p class=dont>" + md_inline(dont) + "</p>" if dont else ""}</div></article>')

# ---------- Writing ----------
writing = "".join(f"<li>{md_inline(l[2:])}</li>" for l in section("Content fundamentals").splitlines() if l.startswith("- "))
# Hero art: the slab arrangement from components/Cover, cropped to its coloured half
cover = ('<svg viewBox="488 0 472 288" role="img" aria-label="FLIK brand colours as blocks">'
         '<rect x="504" y="24" width="88" height="136" rx="12" fill="var(--primary-soft)"/>'
         '<rect x="504" y="176" width="88" height="104" rx="12" fill="var(--ribbon-1)"/>'
         '<rect x="608" y="0" width="184" height="288" fill="var(--dark)"/>'
         '<rect x="808" y="0" width="152" height="200" fill="var(--primary)"/>'
         '<rect x="808" y="216" width="152" height="72" fill="var(--ribbon-2)"/>'
         '<rect x="624" y="232" width="88" height="40" rx="12" fill="var(--ribbon-4)"/>'
         '<line x1="700" y1="0" x2="700" y2="216" stroke="var(--surface)" stroke-width="1.5"/>'
         '<line x1="884" y1="0" x2="884" y2="288" stroke="var(--surface)" stroke-width="1.5"/></svg>')
counts = sum(len(v) for v in comps.values())

# ---------- Partner logos (payment and courier) ----------
PARTNER_NAMES = {"bca": "BCA", "bni": "BNI", "bri": "BRI", "bsi": "BSI", "mandiri": "Mandiri", "permata": "Permata", "dana": "DANA",
                 "gopay": "GoPay", "ovo": "OVO", "qris": "QRIS", "shopeepay": "ShopeePay", "anteraja": "AnterAja", "deliveree": "Deliveree",
                 "gosend": "GoSend", "grabexpress": "GrabExpress", "idexpress": "ID Express", "jne": "JNE", "jnt": "J&T Express",
                 "lalamove": "Lalamove", "lionparcel": "Lion Parcel", "mrspeedy": "Mr. Speedy", "ninjaxpress": "Ninja Xpress", "paxel": "Paxel",
                 "rpx": "RPX", "sap": "SAP Express", "sicepat": "SiCepat", "spx": "SPX Express", "tiki": "TIKI", "wahana": "Wahana",
                 "blibli": "Blibli", "googleads": "Google Ads", "lazada": "Lazada", "magento1": "Magento 1", "magento2": "Magento 2",
                 "metaads": "Meta Ads", "shopee": "Shopee", "shopify": "Shopify", "tiktok": "TikTok", "tokopedia": "Tokopedia",
                 "woocommerce": "WooCommerce", "zalora": "Zalora"}
partners_html = ""
merchants = json.load(open(P("assets", "Logos", "merchant", "merchants.json")))
merchants_html = ('<h3 id="merchant-logos">Merchant logos</h3><p class="x-lead">Brands that sell with FLIK, for the trusted-by strip. '
                  'Shown in greyscale in the strip; use only with the brand\'s permission.</p><div class="mlogos">' + "".join(
    f'<div class="ml{" dk" if m["light"] else ""}"><img src="assets/Logos/merchant/{m["file"]}" alt="{esc(m["name"])}"><span>{esc(m["name"])}</span></div>'
    for m in merchants) + "</div>")
for kind, title in (("payment", "Payment"), ("courier", "Couriers"), ("platform", "Platforms")):
    files = sorted(f[:-4] for f in os.listdir(P("assets", "Logos", kind)) if f.endswith(".png"))
    partners_html += f'<h3>{title}</h3><div class="plogos">' + "".join(
        f'<div class="fl-pm"><img class="fl-plogo fl-plogo--lg" src="assets/Logos/{kind}/{k}.png" alt="">'
        f'<span>{esc(PARTNER_NAMES.get(k, k))}<code>{kind}/{k}.png</code></span></div>' for k in files) + "</div>"

PAGE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FLIK Design System</title>
<meta name="description" content="Colours, type, shapes and components for the FLIK website and merchant dashboard.">
<link rel="icon" href="assets/Logos/flik-mark.svg">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="components/bundle.css">
<style>
/* Page chrome only (x- prefix keeps it clear of the type classes in tokens.css). Everything inside .stage is the real design system. */
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:76px}}
body{{margin:0;font-family:var(--font-sans);color:var(--app-text);background:var(--surface);-webkit-font-smoothing:antialiased;font-size:15px;line-height:1.55}}
a{{color:var(--primary)}}
code{{font-family:var(--font-mono);font-size:.86em;background:var(--app-field);padding:1px 5px;border-radius:4px;color:var(--app-ink)}}
.top{{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--app-line)}}
.top .in{{max-width:1180px;margin:0 auto;padding:0 24px;height:60px;display:flex;align-items:center;gap:20px}}
.top img{{height:24px;display:block}}
.top .t{{font-weight:600;color:var(--app-ink);white-space:nowrap}}
.top nav{{display:flex;gap:4px;margin-left:auto;overflow-x:auto;scrollbar-width:none}}
.top nav a{{color:var(--app-muted);text-decoration:none;font-weight:500;font-size:14px;padding:7px 11px;border-radius:999px;white-space:nowrap}}
.top nav a:hover{{background:var(--app-hover);color:var(--app-ink)}}
.x-hero{{position:relative;overflow:hidden;border-bottom:1px solid var(--app-line)}}
.x-hero .in{{max-width:1180px;margin:0 auto;padding:72px 24px 64px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:40px;align-items:center}}
.x-hero h1{{font-size:52px;line-height:1.08;font-weight:400;letter-spacing:-1.4px;color:var(--ink);margin:0}}
.x-hero h1 span{{color:var(--muted)}}
.x-hero p{{font-size:19px;line-height:1.5;font-weight:300;color:var(--muted);margin:20px 0 0;max-width:520px}}
.x-hero .stats{{display:flex;gap:28px;margin-top:28px;flex-wrap:wrap}}
.x-hero .stats b{{display:block;font-size:28px;font-weight:400;color:var(--ink)}}
.x-hero .stats span{{font-size:13px;color:var(--muted)}}
.x-hero .cover svg{{width:100%;height:auto;display:block}}
.ribbon{{height:6px;background:linear-gradient(90deg,var(--ribbon-1) 0 38%,var(--ribbon-2) 58%,var(--ribbon-3) 80%,var(--ribbon-4))}}
main{{max-width:1180px;margin:0 auto;padding:0 24px 96px}}
section.s{{padding-top:72px}}
section.s>h2{{font-size:34px;font-weight:300;letter-spacing:-.8px;color:var(--ink);margin:0}}
section.s>.x-lead{{font-size:17px;color:var(--muted);margin:10px 0 0;max-width:720px}}
h3{{font-size:18px;font-weight:600;color:var(--app-ink);margin:40px 0 4px}}
.gd{{color:var(--app-muted);margin:0 0 14px;font-size:14px}}
.us{{color:var(--app-muted);font-size:13px;line-height:1.45}}
/* colours */
.rule{{margin-top:24px;padding:16px 20px;border-radius:12px;background:var(--primary-soft);color:var(--app-ink);font-size:15px;max-width:860px}}
.rule b{{color:var(--primary)}}
.pal{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:28px}}
.sws{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}}
.sw{{all:unset;cursor:pointer;display:flex;flex-direction:column;gap:4px;border-radius:12px;padding:8px 8px 12px;box-shadow:var(--app-shadow);background:#fff;transition:transform .15s,box-shadow .15s}}
.sw:hover{{transform:translateY(-2px);box-shadow:var(--shadow-hover)}}
.sw:focus-visible{{box-shadow:var(--focus-ring)}}
.sw .chip{{height:64px;border-radius:8px;display:flex;align-items:flex-end;padding:8px 10px;font-family:var(--font-mono);font-size:12px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06);margin-bottom:6px}}
.sw.big .chip{{height:132px;font-size:13px}}
.sw .nm{{font-weight:600;color:var(--app-ink);padding:0 4px;font-size:14px}}
.sw .us{{padding:0 4px}}
/* type */
.types{{display:grid;border-top:1px solid var(--app-line)}}
.ty{{display:grid;grid-template-columns:260px minmax(0,1fr);gap:24px;padding:20px 0;border-bottom:1px solid var(--app-line);align-items:center}}
.ty .meta{{display:grid;gap:2px}}
.ty .meta b{{color:var(--app-ink);font-weight:600}}
.ty .meta>span:not(.us){{font-size:13px;color:var(--app-text)}}
.ty .sample{{color:var(--ink);overflow-wrap:anywhere}}
/* shapes */
.shapes{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px}}
.shp{{display:grid;gap:3px;align-content:start}}
.shp .box{{height:84px;background:var(--primary-soft);border:1.5px solid var(--primary);margin-bottom:8px}}
.shp .box.sh{{background:#fff;border:0;border-radius:10px;margin:8px 8px 14px}}
.shp b{{color:var(--app-ink);font-size:14px}}.shp>span:not(.us){{font-size:13px}}
.spaces{{display:grid;gap:10px}}
.sp{{display:grid;grid-template-columns:150px 70px auto;gap:6px 14px;align-items:center}}
.sp b{{color:var(--app-ink);font-size:14px}}.sp .v{{font-family:var(--font-mono);font-size:12.5px}}
.sp .bar{{height:12px;border-radius:3px;background:var(--primary)}}
.sp .us{{grid-column:1/-1;margin-top:-4px;padding-bottom:6px;border-bottom:1px solid var(--app-line)}}
/* components */
.cnav{{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}}
.cnav a{{text-decoration:none;font-size:14px;font-weight:500;padding:7px 13px;border-radius:999px;box-shadow:var(--app-shadow);color:var(--app-text)}}
.cnav a:hover{{color:var(--primary)}}
.cp{{border-radius:14px;box-shadow:var(--app-shadow);margin:16px 0 22px;overflow:hidden;background:#fff}}
.cp header{{padding:18px 22px 14px}}
.cp h4{{margin:0;font-size:17px;font-weight:600;color:var(--app-ink)}}
.cp header p{{margin:4px 0 0;color:var(--app-muted);font-size:14.5px;max-width:820px}}
.cp .stage{{padding:28px 24px;background:repeating-conic-gradient(var(--app-hover) 0% 25%,#fff 0% 50%) 0 0/18px 18px;border-top:1px solid var(--app-line);border-bottom:1px solid var(--app-line);overflow-x:auto}}
.cp .stage>*{{background:#fff}}
.cp .stage>.fl{{padding:16px;border-radius:10px;box-shadow:0 0 0 1px var(--app-line)}}
.cp .rules{{padding:14px 22px 18px;display:grid;gap:8px;font-size:14px;color:var(--app-text)}}
.cp .rules p{{margin:0}}
.cp .rules .dont{{color:var(--app-muted)}}
/* logos */
.logos{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:24px}}
.logo{{border-radius:12px;box-shadow:var(--app-shadow);height:150px;display:flex;align-items:center;justify-content:center}}
.logo img{{max-height:44px;max-width:70%}}
.logo.dk{{background:var(--dark)}}
.logo.dk .tile{{background:#fff;border-radius:10px;padding:10px;display:flex}}
.logo.dk .tile img{{height:32px}}
.mlogos{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-top:12px}}.ml{{border-radius:8px;box-shadow:var(--app-shadow);height:96px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:10px}}.ml img{{max-height:32px;max-width:85%}}.ml span{{font-size:12px;color:var(--app-muted)}}.ml.dk{{background:var(--dark)}}.ml.dk span{{color:var(--on-dark-muted)}}
.plogos{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 20px;margin-top:12px}}.plogos .fl-pm span{{display:flex;flex-direction:column;font-size:14px;color:var(--app-ink)}}.plogos code{{font:12px var(--font-mono,monospace);color:var(--app-muted)}}
.logo-cap{{font-size:13px;color:var(--app-muted);margin-top:8px}}
/* writing */
.write{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;padding:0;list-style:none;margin:28px 0 0}}
.write li{{border-radius:12px;background:var(--app-hover);padding:18px 20px;font-size:15px}}
.write li b{{color:var(--app-ink)}}
footer{{border-top:1px solid var(--app-line);color:var(--app-muted);font-size:14px}}
footer .in{{max-width:1180px;margin:0 auto;padding:28px 24px;display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between}}
.copied{{position:fixed;left:50%;bottom:24px;transform:translate(-50%,16px);background:var(--app-ink);color:#fff;padding:10px 16px;border-radius:8px;font-size:14px;opacity:0;transition:.2s;pointer-events:none;z-index:50}}
.copied.on{{opacity:1;transform:translate(-50%,0)}}
@media (max-width:900px){{
  .x-hero .in{{grid-template-columns:1fr;padding:48px 16px 40px}}.x-hero h1{{font-size:38px}}
  .top .in,main,footer .in{{padding-left:16px;padding-right:16px}}
  .pal{{grid-template-columns:repeat(2,1fr)}}.logos,.write,.plogos{{grid-template-columns:1fr 1fr}}.mlogos{{grid-template-columns:repeat(3,1fr)}}
  .ty{{grid-template-columns:1fr;gap:8px}}.ty .sample{{font-size:min(100%,34px)}}
}}
@media (max-width:560px){{.top .t{{display:none}}.pal,.logos,.write{{grid-template-columns:1fr}}.sp{{grid-template-columns:1fr 70px}}.sp .bar{{grid-column:1/-1}}}}
</style>
</head>
<body>
<header class="top"><div class="in"><img src="assets/Logos/flik-wordmark.svg" alt="FLIK"><span class="t">Design System</span>
<nav><a href="#colours">Colours</a><a href="#type">Type</a><a href="#shapes">Shapes</a><a href="#components">Components</a><a href="#logo">Logo</a><a href="#writing">Writing</a></nav></div></header>

<div class="x-hero"><div class="in"><div>
<h1>FLIK Design System. <span>One look for the website and the dashboard.</span></h1>
<p>The colours, type, shapes and building blocks every FLIK page is made of. Click any colour to copy its code.</p>
<div class="stats"><div><b>{len(tokens["color"]["tokens"])}</b><span>colours</span></div><div><b>{sum(len(g["styles"]) for g in tokens["type"]["groups"])}</b><span>text styles</span></div><div><b>{counts}</b><span>components</span></div></div>
</div><div class="cover">{cover}</div></div><div class="ribbon"></div></div>

<main>
<section class="s" id="colours"><h2>Colours</h2><p class="x-lead">Five brand colours. Violet is the only colour for things people click; navy carries the text; cyan, magenta and orange live in the brand ribbon.</p>
<div class="rule"><b>Use only these colours.</b> Every colour on a FLIK page or in the dashboard comes from this list. No other colours, no new tints or shades, and no gradients except the brand ribbon. Bank, e-wallet, card and courier logos keep their own colours. Need a new colour? Ask for it to be added here first.</div>
{color_html}</section>

<section class="s" id="type"><h2>Type</h2><p class="x-lead">One typeface, Inter, everywhere. Website headings are large and light; the dashboard is smaller and bolder so tables stay easy to scan.</p>
{type_html}</section>

<section class="s" id="shapes"><h2>Shapes, depth and spacing</h2><p class="x-lead">Small corners on buttons, bigger ones on cards. Soft shadows instead of hard borders.</p>
{shape_html}</section>

<section class="s" id="components"><h2>Components</h2><p class="x-lead">Every piece below is live, built from the real styles. Each one says when to use it and what to avoid.</p>
<div class="rule"><b>Reuse first.</b> Always build with these components. Combine and configure what is here before making anything new. If nothing fits, the new piece is added to this design system (with an example and rules) and approved before it is used. No one-off buttons, cards, tables or badges.</div>
<div class="cnav">{"".join(f'<a href="#{i}">{esc(t)}</a>' for i, t in comp_nav)}</div>
{comp_html}</section>

<section class="s" id="logo"><h2>Logo</h2><p class="x-lead">Always use the real files; never redraw, recolour or stretch them. On a dark background, put the F mark on a white tile.</p>
<div class="logos"><div><div class="logo"><img src="assets/Logos/flik-wordmark.svg" alt="FLIK wordmark"></div><p class="logo-cap">Wordmark, on white. Header of every page.</p></div>
<div><div class="logo" style="background:var(--surface-alt)"><img src="assets/Logos/flik-wordmark.svg" alt="FLIK wordmark"></div><p class="logo-cap">Wordmark, on the light grey band.</p></div>
<div><div class="logo"><img src="assets/Logos/flik-mark.svg" alt="FLIK F mark"></div><p class="logo-cap">F mark: app icon, account switcher.</p></div>
<div><div class="logo dk"><span class="tile"><img src="assets/Logos/flik-mark.svg" alt="FLIK F mark"></span></div><p class="logo-cap">F mark on a white tile, on navy.</p></div></div>
<h3 id="partner-logos">Partner logos</h3><p class="x-lead">Bank, e-wallet, QRIS, courier and platform logos, shown with the <a href="#c-PartnerLogo">PartnerLogo</a> tile. They keep their own colours. Use the PNG files.</p>{partners_html}{merchants_html}</section>

<section class="s" id="writing"><h2>Writing</h2><p class="x-lead">How FLIK sounds, on the website and in the dashboard.</p>
<ul class="write">{writing}</ul></section>
</main>

<footer><div class="in"><span>FLIK Design System · v4 palette</span><span><a href="https://github.com/raam-flik/flik-design-system">Files on GitHub</a> · <a href="tailwind/index.html">Tailwind version</a> · <a href="https://landing-page-raams-projects-2709477f.vercel.app/dashboard/">Live dashboard</a></span></div></footer>
<div class="copied" id="copied"></div>
<script>
// Click a colour to copy its hex code; demo buttons inside the stages do nothing.
const tip=document.getElementById('copied');let tt;
document.addEventListener('click',e=>{{
  const sw=e.target.closest('[data-copy]');
  if(sw){{const v=sw.dataset.copy;(navigator.clipboard?navigator.clipboard.writeText(v):Promise.reject()).catch(()=>{{}});tip.textContent='Copied '+v;tip.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>tip.classList.remove('on'),1600);return}}
  if(e.target.closest('.stage a,.stage button'))e.preventDefault();
}});
</script>
</body>
</html>
'''
open(P("index.html"), "w").write(PAGE)
print(f"index.html written: {len(tokens['color']['tokens'])} colours, {counts} components")
