"""Prepare merchant logos for the web.

Usage: python3 scripts/prep_merchant_logos.py assets/Logos/merchant

Reads every file in <dir>/original/, writes <dir>/<slug>.png (trimmed, at most
96px tall / 480px wide, transparent background where the source had a plain
white one) and <dir>/merchants.json (slug, display name, source file, flags).
"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw

D = Path(sys.argv[1])
SRC = D / "original"

# Display names (proper brand spelling); keys are the cleaned file stems
NAMES = {
    "25h": "25H", "andall": "Andall", "aneka": "Aneka", "arm-sports": "ARM Sports", "artch": "Artch",
    "baggy-apparel": "Baggy Apparel", "bia": "BIA", "booyah": "Booyah", "byelice": "Byelice", "cottonology": "Cottonology",
    "carvil": "Carvil", "dauky": "Dauky", "davclar": "Davclar", "emrys": "Emrys", "evo-plusmed": "Evo Plusmed",
    "elzatta": "Elzatta", "fieri": "Fieri", "gently": "Gently", "green-andara-residences": "Green Andara Residences",
    "gula-paws": "Gula Paws", "geraihawa": "Geraihawa", "hanoon": "Hanoon", "hoya-fields": "Hoya Fields",
    "julie-mango": "Julie Mango", "jamise": "Jamise", "kuvings": "Kuvings", "liga-arloji": "Liga Arloji",
    "fertig-white": "Fertig (white)", "fertig": "Fertig", "m-gee": "M. Gee", "mayora": "Mayora", "milidi-dower": "Milidi Dower",
    "mpy": "MPY", "my-love": "My Love", "mytee": "Mytee", "ogre": "Ogre", "oxygen-denim": "Oxygen Denim",
    "petshop-indonesia": "Petshop Indonesia", "petsantuy": "Petsantuy", "posterq": "PosterQ", "roughneck": "Roughneck",
    "ryusei-white": "Ryusei (white)", "ryusei": "Ryusei", "sadia": "Sadia", "sanip-tiraka": "Sanip Tiraka",
    "sol-et-terre": "Sol et Terre", "solcare": "Solcare", "sunrise": "Sunrise", "susu-fitnessku": "Susu Fitnessku",
    "style-cycle": "Style Cycle", "teratu-beauty": "Teratu Beauty", "trooper": "Trooper", "two-mix": "Two Mix",
    "xtart": "Xtart", "yesamalika": "Yesamalika", "zmnow": "ZMNow", "gakmikir": "Gakmikir", "gio-cardin": "Gio Cardin",
    "happyfeet": "Happyfeet", "kado-unik": "Kado Unik", "kaffah-sentral-indonesia": "Kaffah Sentral Indonesia",
    "key-by-keira-shabira": "Key by Keira Shabira", "keychron": "Keychron", "cempaka-variasi": "Cempaka Variasi",
    "emandos": "Emandos", "luma-dawa": "Luma Dawa", "makeblock": "Makeblock", "meccanism": "Meccanism", "minaku": "Minaku",
    "moire": "Moire", "myfirst": "myFirst", "nehhat": "Nehhat", "northy": "Northy", "nuphy": "NuPhy", "occa": "Occa",
    "qnq": "QnQ", "sevenrose": "Sevenrose", "skandi": "Skandi", "soru": "Soru", "stetoskop-id": "Stetoskop ID",
    "third-day": "Third Day", "vincencio": "Vincencio", "zaafer": "Zaafer", "zeero": "Zeero",
}


# White shapes with dark text: they read fine on white, so they're not light logos
NOT_LIGHT = {"soru"}


def slug_of(name):
    s = Path(name).stem.lower()
    s = re.sub(r"@3x|\bcopy\b|\(1\)|\bhitam\b|\bblack logo\b|\bblack\b|\blogo\b|-logo-ico|\bred\b|_logo|logo-|\b2\b|\b1\b", " ", s)
    s = s.replace("m. gee", "m gee")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return {"teratu-beauty": "teratu-beauty", "qnqlogo": "qnq", "skandilogo": "skandi", "myfirst": "myfirst"}.get(s, s)


def clear_white_bg(im, tol=24):
    """Flood-fill a plain near-white background from the corners to transparent."""
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    if not all(c[3] > 250 and min(c[:3]) > 235 for c in corners):
        return im, False
    mask = Image.new("L", (w, h), 0)
    rgb = im.convert("RGB")
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(rgb, (x, y), (255, 0, 255), thresh=tol)
    r, g, b = rgb.split()
    data = [255 if (pr, pg, pb) == (255, 0, 255) else 0 for pr, pg, pb in zip(r.getdata(), g.getdata(), b.getdata())]
    mask.putdata(data)
    a = im.split()[3].point(lambda v: v)
    a.paste(0, mask=mask)
    im.putalpha(a)
    return im, True


def main():
    out, seen = [], set()
    for f in sorted(SRC.iterdir()):
        if f.name.startswith("."):
            continue
        slug = slug_of(f.name)
        assert slug in NAMES, f"no display name for {slug!r} ({f.name})"
        assert slug not in seen, f"duplicate slug {slug}"
        seen.add(slug)
        im = Image.open(f).convert("RGBA")
        opaque = im.split()[3].getextrema()[0] > 250
        cleared = False
        if opaque:
            im, cleared = clear_white_bg(im)
        bbox = im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox() or (0, 0, *im.size)
        im = im.crop(bbox)
        w, h = im.size
        scale = min(1.0, 96 / h, 480 / w)
        if scale < 1:
            im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        # light logos (mostly white ink) are for dark backgrounds
        rgba = list(im.getdata())
        ink = [p for p in rgba if p[3] > 128]
        light = bool(ink) and sum(min(p[:3]) for p in ink) / len(ink) > 215
        light = light and slug not in NOT_LIGHT
        im.save(D / f"{slug}.png", optimize=True)
        solid = opaque and not cleared
        out.append({"slug": slug, "name": NAMES[slug], "file": f"{slug}.png", "source": f"original/{f.name}",
                    "width": im.size[0], "height": im.size[1], "background": "solid" if solid else "transparent",
                    "light": light})
    (D / "merchants.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    for m in out:
        print(f"{m['slug']:28} {m['width']:>3}x{m['height']:<3} {m['background']:11} {'LIGHT' if m['light'] else ''}  <- {m['source']}")


if __name__ == "__main__":
    main()
