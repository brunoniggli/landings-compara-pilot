#!/usr/bin/env python3
"""
Sube CSS, JS, fuentes e imágenes al File Manager de HubSpot.

Por qué existe: hasta ahora esos assets se servían desde un repo de GitHub en una cuenta
personal, así que las landings en producción dependían de esa cuenta. Con el scope `files`
activo (2026-07-30) van al File Manager, que además usa el CDN de HubSpot, más rápido que
GitHub Pages: la diferencia de LCP que quedaba en la landing de Auto era justo eso.

Ojo: el CSS y el JS siguen siendo archivos EXTERNOS, no inline. Inlinearlos empeora el
DOMContentLoaded 4x (medido) y rompe el cache compartido entre las 23 landings.

Uso:
    python3 _docs/hubspot_upload_assets.py            # dry-run, lista qué subiría
    python3 _docs/hubspot_upload_assets.py --apply
"""
import json, urllib.request, urllib.error, uuid, pathlib, sys, mimetypes, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = "/landings-compara"          # carpeta en el File Manager
TOK = [l.split("=",1)[1].strip().strip('"').strip("'") for l in
       open(pathlib.Path.home()/"ClaudeCode/Claudia/.secrets/hubspot.env")
       if l.startswith("HUBSPOT_TOKEN=")][0]

# qué se sube y a qué subcarpeta. El CSS se reescribe al vuelo para que las @font-face
# apunten al File Manager en vez de a rutas relativas del repo.
# El orden importa: las fuentes van primero porque colors_and_type.css referencia
# ./fonts/... y hay que reescribir esas rutas con la URL real del File Manager.
GRUPOS = [
    ("brand/design-system/fonts/*.woff2",       "fonts"),
    ("brand/design-system/colors_and_type.css", "css"),
    ("shared/compara.css",                      "css"),
    # Hoja exclusiva de Auto/CICL: es la versión que ganó el A/B y no comparte hoja con
    # las de New Business. Ver ESPECIALES en hubspot_template.py.
    ("shared/compara-auto.css",                 "css"),
    ("shared/compara.js",                       "js"),
    ("brand/design-system/assets/*.svg",        "img"),
    ("brand/design-system/assets/*.png",        "img"),
    ("assets/*.svg",                            "img"),
    ("assets/auto-opt/*.webp",                  "img"),
]

def subir(path: pathlib.Path, sub: str, contenido: bytes = None):
    data = contenido if contenido is not None else path.read_bytes()
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if path.suffix == ".woff2": ctype = "font/woff2"
    if path.suffix == ".webp":  ctype = "image/webp"
    if path.suffix == ".js":    ctype = "application/javascript"
    bnd = "----" + uuid.uuid4().hex
    partes = []
    def add(name, value, filename=None, ct=None):
        h = f'--{bnd}\r\nContent-Disposition: form-data; name="{name}"'
        if filename: h += f'; filename="{filename}"'
        h += "\r\n"
        if ct: h += f"Content-Type: {ct}\r\n"
        partes.append(h.encode() + b"\r\n" + (value if isinstance(value, bytes) else value.encode()) + b"\r\n")
    add("file", data, path.name, ctype)
    add("options", json.dumps({"access": "PUBLIC_INDEXABLE", "overwrite": True}))
    add("folderPath", f"{DEST}/{sub}")
    body = b"".join(partes) + f"--{bnd}--\r\n".encode()
    req = urllib.request.Request("https://api.hubapi.com/files/v3/files", method="POST", data=body,
            headers={"Authorization": f"Bearer {TOK}",
                     "Content-Type": f"multipart/form-data; boundary={bnd}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["url"]

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    archivos = []
    for patron, sub in GRUPOS:
        if "*" in patron:
            archivos += [(p, sub) for p in sorted(ROOT.glob(patron))]
        else:
            p = ROOT / patron
            if p.exists(): archivos.append((p, sub))
    total_kb = sum(p.stat().st_size for p, _ in archivos) / 1024
    print(f"{'DRY-RUN' if not apply else 'SUBIENDO'} | {len(archivos)} archivos | {total_kb:.0f}KB")
    if not apply:
        for p, sub in archivos[:6]:
            print(f"   {sub}/{p.name}  ({p.stat().st_size/1024:.0f}KB)")
        print(f"   ... y {len(archivos)-6} más\nCorrer con --apply para subir.")
        sys.exit(0)
    urls = {}
    for i, (p, sub) in enumerate(archivos, 1):
        try:
            # el colors_and_type.css referencia ./fonts/... : hay que reescribirlo
            contenido = None
            if p.name == "colors_and_type.css":
                base_fonts = urls.get("__fonts_base__")
                assert base_fonts, "las fuentes tienen que subirse antes del CSS"
                # RELATIVO, no absoluto: HubSpot reescribe las URLs del HTML al dominio de
                # la página pero NO las de dentro del CSS. Con URL absoluta al CDN, el
                # preload (reescrito) y el @font-face (sin reescribir) apuntan a hosts
                # distintos y el navegador baja las fuentes DOS veces: 95KB de más en la
                # ruta crítica. Con ../fonts/ se resuelve contra el host del propio CSS,
                # así que siempre coincide.
                contenido = p.read_text().replace('url("./fonts/', 'url("../fonts/').encode()
            u = subir(p, sub, contenido)
            urls[f"{sub}/{p.name}"] = u
            if sub == "fonts" and "__fonts_base__" not in urls:
                urls["__fonts_base__"] = u.rsplit("/", 1)[0] + "/"
            print(f"   [{i:>3}/{len(archivos)}] {sub}/{p.name}")
        except urllib.error.HTTPError as e:
            print(f"   ERRO {sub}/{p.name}: {e.code} {e.read().decode()[:120]}")
        time.sleep(0.15)
    json.dump(urls, open("/tmp/hubspot-asset-urls.json", "w"), indent=1)
    base = urls.get("css/compara.css", "")
    print(f"\nsubidos {len([k for k in urls if not k.startswith('__')])} archivos")
    print(f"base del CDN: {base.rsplit('/',2)[0] if base else '?'}/")
