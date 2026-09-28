#!/usr/bin/env python3
"""Build the Anino Welding Kenya static site.

    python3 tools/build.py

Reads src/pages/*.html, wraps each in the shared header/footer from
src/partials/, fills {{TOKENS}} from SITE below, renders the gallery from
assets/img/gallery/gallery.json, and writes everything to dist/.

No dependencies beyond the Python 3 standard library.
"""
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

# ---------------------------------------------------------------------------
# Business details — edit here, rebuild, done.
# ---------------------------------------------------------------------------
SITE = {
    "NAME": "Anino Welding Kenya",
    "SHORT_NAME": "Anino Welding",
    "PHONE_DISPLAY": "0741 700 573",
    "PHONE_INTL": "+254 741 700 573",
    "PHONE_TEL": "+254741700573",
    "WA_NUMBER": "254741700573",
    # TODO(client): email not yet confirmed. Replace, rebuild, redeploy.
    "EMAIL": "info@aninowelding.com",
    "LOCATION": "Syokimau",
    "LOCATION_LONG": "Workshop in Syokimau — serving clients across Kenya and abroad",
    "HOURS": "Mon – Sat, 8:00am – 6:00pm",
    "DOMAIN": "https://aninowelding.com",
}
WA_DEFAULT_MSG = "Hello Anino Welding, I would like a quote for "


def wa_link(msg=WA_DEFAULT_MSG):
    from urllib.parse import quote
    return f"https://wa.me/{SITE['WA_NUMBER']}?text={quote(msg)}"


ICONS = {
    "phone": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1l-2.2 2.2z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.15-1.75-.86-2-.96-.28-.1-.48-.15-.68.15-.2.3-.78.96-.95 1.16-.18.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.13.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.68-1.63-.93-2.23-.24-.58-.49-.5-.68-.51h-.58c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.75-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.04 21.5h-.01a9.4 9.4 0 0 1-4.8-1.32l-.34-.2-3.57.94.95-3.48-.22-.36a9.44 9.44 0 1 1 7.99 4.42zm8.02-17.46A11.3 11.3 0 0 0 12.04.7C5.8.7.72 5.78.72 12.02c0 2 .52 3.94 1.51 5.66L.63 23.3l5.77-1.51a11.3 11.3 0 0 0 5.64 1.44h.01c6.24 0 11.32-5.08 11.32-11.32 0-3.02-1.18-5.87-3.31-8z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    # service icons
    "gate": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21V5M21 21V5M3 8h18M3 18h18M7 8v10M11 8v10M15 8v10M19 8v10"/></svg>',
    "door": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 21V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v17M3 21h18M8 7h8v5H8zM15 16h1"/></svg>',
    "window": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18M4 12h16"/></svg>',
    "grill": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M8 3v18M12 3v18M16 3v18M3 9c3-2 6 2 9 0s6-2 9 0M3 15c3-2 6 2 9 0s6-2 9 0"/></svg>',
    "roof": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12L12 4l10 8M5 10v10h14V10M9 20v-5h6v5"/></svg>',
    "wrench": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.2L3 17.8V21h3.2l6.3-6.3a4 4 0 0 0 5.2-5.4l-2.6 2.6-2.4-.6-.6-2.4 2.6-2.6z"/></svg>',
    "stairs": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h5v-5h5v-5h5V6h3M3 12l9-9"/></svg>',
    "tank": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 4h12v9H6zM6 13l-2 8M18 13l2 8M9 13l-1 8M15 13l1 8M4 17h16"/></svg>',
    "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "ruler": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 17L17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 6h12v10H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>',
    "logo": '<svg viewBox="0 0 48 48" aria-hidden="true"><rect width="48" height="48" rx="10" fill="#111418"/><path d="M12 36L24 10l12 26" fill="none" stroke="#f26a1b" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M17 28h14" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/><circle cx="36" cy="13" r="2.2" fill="#f26a1b"/><path d="M33 9l-1.5-2M39 10l2-1.5M38 16l2 1" stroke="#f26a1b" stroke-width="1.6" stroke-linecap="round"/></svg>',
}

NAV = [
    ("home", "index.html", "Home"),
    ("services", "services.html", "Services"),
    ("gallery", "gallery.html", "Gallery"),
    ("about", "about.html", "About"),
    ("contact", "contact.html", "Contact"),
]

HOME_MOSAIC = {"p04", "p18", "p01", "p11", "p08"}

GALLERY_CATEGORIES = {
    "gates": "Gates",
    "doors": "Doors",
    "windows": "Windows",
    "grills": "Grills & Balconies",
    "roofing": "Structures & Roofing",
    "repairs": "Repairs",
    "other": "Other Work",
}


def load_gallery():
    path = ROOT / "assets" / "img" / "gallery" / "gallery.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def render_gallery(items, limit=None, with_filters=False):
    if not items:
        n = limit or 8
        tiles = "\n".join(f'      <div class="gallery__placeholder">Photo coming soon</div>' for _ in range(n))
        return f'<div class="gallery">\n{tiles}\n    </div>'

    shown = items[:limit] if limit else items
    parts = []
    if with_filters:
        present = [c for c in GALLERY_CATEGORIES if any(i["category"] == c for i in items)]
        if len(present) > 1:
            btns = ['<button type="button" data-filter="all" aria-pressed="true">All work</button>']
            btns += [
                f'<button type="button" data-filter="{c}" aria-pressed="false">{GALLERY_CATEGORIES[c]}</button>'
                for c in present
            ]
            parts.append('<div class="filters" role="group" aria-label="Filter photos">' + "".join(btns) + "</div>")
    tiles = []
    for it in shown:
        cap = html.escape(it["caption"])
        label = GALLERY_CATEGORIES.get(it["category"], "")
        tiles.append(
            f'<figure class="tile gallery__item" data-category="{it["category"]}" data-full="{it["full"]}" '
            f'tabindex="0" role="button" aria-label="View larger: {cap}">'
            f'<img src="{it["thumb"]}" width="{it["tw"]}" height="{it["th"]}" alt="{cap}" loading="lazy" decoding="async">'
            f'<figcaption class="tile__cap"><b>{label}</b>{cap}</figcaption></figure>'
        )
    parts.append('<div class="gallery" data-lightbox>\n      ' + "\n      ".join(tiles) + "\n    </div>")
    return "\n    ".join(parts)


def render_nav(active):
    items = []
    for key, href, label in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "\n          ".join(items)


def fill(text, extra):
    tokens = {**SITE, **extra}
    tokens["WA_LINK"] = html.escape(wa_link())
    tokens["YEAR"] = "2026"

    def icon(m):
        return ICONS[m.group(1)]

    text = re.sub(r"\{\{icon:(\w+)\}\}", icon, text)

    def wa_msg(m):
        return html.escape(wa_link(m.group(1)))

    text = re.sub(r"\{\{wa:([^}]+)\}\}", wa_msg, text)

    def tok(m):
        key = m.group(1)
        if key not in tokens:
            raise KeyError(f"Unknown token {{{{{key}}}}}")
        return str(tokens[key])

    # Two passes so tokens inside partials/meta resolve too.
    for _ in range(2):
        text = re.sub(r"\{\{([A-Z_]+)\}\}", tok, text)
    return text


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    layout = (SRC / "partials" / "layout.html").read_text()
    # Cache-bust CSS/JS: assets are cached for 30 days (netlify.toml), so the URL
    # must change whenever the file does.
    for asset in ("assets/css/style.css", "assets/js/main.js"):
        digest = hashlib.sha1((ROOT / asset).read_bytes()).hexdigest()[:8]
        layout = layout.replace(f'"{asset}"', f'"{asset}?v={digest}"')
    gallery = load_gallery()

    for page in sorted((SRC / "pages").glob("*.html")):
        raw = page.read_text()
        m = re.match(r"<!--meta\s+(\{.*?\})\s*-->\s*", raw, re.S)
        if not m:
            raise SystemExit(f"{page.name}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        body = raw[m.end():]

        # Home preview skips the photos already used in the hero mosaic.
        preview = [g for g in gallery if g["id"] not in HOME_MOSAIC] or gallery
        body = body.replace("{{GALLERY_PREVIEW}}", render_gallery(preview, limit=8))
        body = body.replace("{{GALLERY_FULL}}", render_gallery(gallery, with_filters=True))

        canonical = SITE["DOMAIN"] + "/" + ("" if page.name == "index.html" else page.name)
        out = layout.replace("{{CONTENT}}", body)
        out = fill(out, {
            "TITLE": meta["title"],
            "DESCRIPTION": meta["description"],
            "NAV_ITEMS": render_nav(meta.get("nav", "")),
            "CANONICAL": canonical,
            "ROBOTS": meta.get("robots", "index,follow"),
        })
        (DIST / page.name).write_text(out)
        print(f"  built {page.name}")

    # Static assets
    shutil.copytree(ROOT / "assets", DIST / "assets",
                    ignore=shutil.ignore_patterns("gallery.json", ".gitkeep"))
    for f in (SRC / "static").iterdir():
        target = DIST / f.name
        if f.suffix in {".xml", ".txt", ".webmanifest"}:
            target.write_text(fill(f.read_text(), {}))
        else:
            shutil.copy2(f, target)
    (DIST / "favicon.svg").write_text(ICONS["logo"].replace(' aria-hidden="true"', ' xmlns="http://www.w3.org/2000/svg"'))
    print(f"Done → {DIST.relative_to(ROOT)}/  ({len(gallery)} gallery photos)")


if __name__ == "__main__":
    main()
