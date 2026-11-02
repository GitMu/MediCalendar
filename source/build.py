import math, json, os, subprocess, shutil, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.dirname(ROOT)  # racine du dépôt = site publié
RED = "#C8102E"

def snake(sign):
    pts = []
    for i in range(0, 121):
        s = i / 120
        y = 440 - s * 210
        amp = 46 + 30 * s
        x = 256 + sign * amp * math.sin(s * 3.5 * math.pi)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    hx, hy = pts[-1]
    return d, hx, hy

def caduceus(color=RED, halo="#FFFFFF"):
    wing = ("M256,150 C214,116 160,102 92,112 C120,128 140,136 156,142 "
            "C128,146 106,154 88,170 C128,170 156,168 176,170 C156,178 140,188 130,202 "
            "C170,196 210,188 256,186 Z")
    parts = [
        f'<path d="{wing}" fill="{color}"/>',
        f'<path d="{wing}" fill="{color}" transform="translate(512 0) scale(-1 1)"/>',
        f'<rect x="245" y="112" width="22" height="342" rx="11" fill="{color}"/>',
        f'<circle cx="256" cy="102" r="21" fill="{color}"/>',
    ]
    for sign in (1, -1):
        d, hx, hy = snake(sign)
        parts.append(f'<path d="{d}" fill="none" stroke="{halo}" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>')
        parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>')
        # tête tournée vers le bâton
        inward = 1 if hx < 256 else -1
        cx = hx + inward * 12
        rot = -inward * 20
        parts.append(f'<ellipse cx="{cx:.1f}" cy="{hy-6:.1f}" rx="25" ry="16" fill="{halo}" transform="rotate({rot} {cx:.1f} {hy-6:.1f})"/>')
        parts.append(f'<ellipse cx="{cx:.1f}" cy="{hy-6:.1f}" rx="19" ry="11.5" fill="{color}" transform="rotate({rot} {cx:.1f} {hy-6:.1f})"/>')
        parts.append(f'<circle cx="{cx + inward*6:.1f}" cy="{hy-11:.1f}" r="3" fill="{halo}"/>')
    return "".join(parts)

def icon_svg(scale, bg="#FFFFFF", color=RED, halo="#FFFFFF"):
    rect = f'<rect width="512" height="512" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">{rect}'
            f'<g transform="translate(256 262) scale({scale}) translate(-256 -278)">{caduceus(color, halo)}</g></svg>')

def png(svg, out, size):
    tmp = out + ".svg"
    open(tmp, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), tmp, "-o", out], check=True)
    os.remove(tmp)

os.makedirs(os.path.join(DIST, "icons"), exist_ok=True)
icons = os.path.join(DIST, "icons")
open(os.path.join(icons, "icon.svg"), "w").write(icon_svg(0.86))
png(icon_svg(0.86), os.path.join(icons, "icon-192.png"), 192)
png(icon_svg(0.86), os.path.join(icons, "icon-512.png"), 512)
png(icon_svg(0.70), os.path.join(icons, "icon-maskable-512.png"), 512)
png(icon_svg(0.80), os.path.join(icons, "apple-touch-icon.png"), 180)
# icône monochrome pour la barre de notifications Android (silhouette sur fond transparent)
png(icon_svg(0.9, bg=None, color="#FFFFFF", halo="#00000000"), os.path.join(icons, "badge-96.png"), 96)

app = open(os.path.join(ROOT, "app.html")).read()
symbol_inner = '<rect width="512" height="512" fill="#FFFFFF"/>' + \
    f'<g transform="translate(256 262) scale(0.86) translate(-256 -278)">{caduceus()}</g>'
app = app.replace("%CADUCEE%", symbol_inner)

# Aperçu (artifact) : fragment sans service worker
if os.environ.get("PREVIEW_OUT"):
    open(os.environ["PREVIEW_OUT"], "w").write(app)

# Version PWA à héberger
head = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#FFFFFF">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="MediCalendar">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:0}body{margin:0}[hidden]{display:none!important}</style>
<script>window.__MEDICAL_PWA__=true</script>
"""
page = head + app.replace("<div class=\"app\">", "</head>\n<body>\n<div class=\"app\">", 1) + "\n</body>\n</html>\n"
open(os.path.join(DIST, "index.html"), "w").write(page)

manifest = {
    "name": "MediCalendar",
    "short_name": "MediCalendar",
    "description": "Rappels de prise de médicaments et de commande en pharmacie.",
    "lang": "fr",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": "#FFFFFF",
    "theme_color": "#FFFFFF",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
open(os.path.join(DIST, "manifest.webmanifest"), "w").write(json.dumps(manifest, ensure_ascii=False, indent=2))
shutil.copy(os.path.join(ROOT, "sw.js"), os.path.join(DIST, "sw.js"))

print("ok")
