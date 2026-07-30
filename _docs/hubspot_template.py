#!/usr/bin/env python3
"""
Convierte una landing generada (.html) en un TEMPLATE CODEADO de HubSpot,
server-rendered: sin loader, sin fetch, sin espera.

Por qué existe: el montaje anterior inyectaba el HTML con fetch() desde GitHub Pages.
Medido en mobile con red real (3G rápido + CPU 4x), eso dejaba ~430ms de pantalla sin
contenido, y ataba la producción a un repo externo. Con el template codeado el HTML llega
en la primera respuesta del servidor.

Qué va inline: SOLO el HTML de la landing. El CSS y el JS quedan como <link>/<script src>
al CDN, a propósito.

Por qué NO se inlinea el CSS/JS, con números: la primera versión de este script metía
colors_and_type.css + compara.css + compara.js inline (~62KB sin minificar). Medido en
mobile 3G rápido con CPU 4x, eso empeoró todo 4x: la espera después de DOMContentLoaded
bajó de 486ms a 29ms (el fetch murió, como se esperaba), pero el DOMContentLoaded mismo
pasó de 682ms a 4717ms, porque 51KB de CSS inline bloquean el render y el parse con CPU
throttled es caro. Resultado: H1 visible pasó de 1168ms a 4746ms.

Con <link> externo se gana dos veces: el render no se bloquea con el HTML, y las 22
landings comparten el mismo CSS, así que a partir de la segunda página el navegador lo
sirve de cache. Inline, cada landing vuelve a bajar los 51KB.

Los assets binarios (fuentes .ttf, logos) siguen en GitHub Pages. Subirlos al File Manager
de HubSpot requiere el scope `files`, que el token compartido no tiene (da 403).

Uso:
    python3 _docs/hubspot_template.py salud-complementario     # imprime el template
    python3 _docs/hubspot_template.py salud-complementario -o /tmp/t.html
"""
import pathlib, re, sys, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSET_BASE = "https://brunoniggli.github.io/landings-compara-pilot/"

def absolutizar(txt: str) -> str:
    """Rutas relativas de assets -> absolutas. En el template no hay documento base."""
    txt = re.sub(r'(src|href)="(brand/|assets/)', rf'\1="{ASSET_BASE}\2', txt)
    txt = re.sub(r'srcset="(brand/|assets/)', rf'srcset="{ASSET_BASE}\1', txt)
    return txt

def css_con_fuentes_absolutas() -> str:
    """colors_and_type.css usa ./fonts/... — hay que reescribirlo al CDN."""
    css = (ROOT/"brand/design-system/colors_and_type.css").read_text(encoding="utf-8")
    return css.replace('url("./fonts/', f'url("{ASSET_BASE}brand/design-system/fonts/')

def build(slug: str) -> str:
    src = (ROOT/f"{slug}.html").read_text(encoding="utf-8")

    # --- del archivo fuente saco solo lo que va al template
    title = re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip()
    desc  = re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1).strip()
    body  = re.search(r"<body>(.*)</body>", src, re.S).group(1)

    # el <script> final (redirección con gclid/utm) se conserva; los <script src> se
    # reemplazan por la versión inline, así no hay requests extra ni orden frágil
    redirect = re.search(r"<script>\s*(/\*.*?\*/\s*\(function\(\)\{.*?\}\)\(\);)\s*</script>",
                         body, re.S)
    if not redirect:
        raise SystemExit(f"{slug}: no encontré el script de redirección")
    redirect_js = redirect.group(1)

    # saco del body: skip-link (lo esconde el tema igual), los <script src> y el script inline
    body = re.sub(r'<a class="skip-link".*?</a>\s*', "", body, flags=re.S)
    body = re.sub(r'<script src="[^"]*"[^>]*></script>\s*', "", body)
    body = re.sub(r"<script>.*?</script>\s*", "", body, flags=re.S)
    body = absolutizar(body).strip()

    VER = re.search(r'VER = "([^"]+)"', (ROOT/"_docs/generate.py").read_text()).group(1)

    # OJO: el primer comentario del archivo lo parsea HubSpot como YAML de metadata.
    # Solo claves ahí; cualquier texto libre rompe el POST con "Unable to process
    # annotated template metadata". La documentación va en un segundo comentario.
    return f"""<!--
  templateType: page
  isAvailableForNewContent: false
  label: Landing {slug} server-rendered
-->
<!--
  Generado por _docs/hubspot_template.py desde {slug}.html. NO editar acá: editar el
  contenido en _docs/generate.py, regenerar y volver a subir el template.

  Server-rendered a propósito: el HTML llega en la primera respuesta, sin el fetch() que
  dejaba ~430ms de pantalla vacía en mobile con red real.

  standard_header_includes / standard_footer_includes se mantienen: inyectan el tracking
  del portal y el headHtml de la página, donde viven GTM, AB Tasty y el noindex.
-->
<!doctype html>
<html lang="es" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{ASSET_BASE}brand/design-system/assets/avatar_favicon.svg">
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="stylesheet" href="{ASSET_BASE}brand/design-system/colors_and_type.css?v={VER}">
<link rel="stylesheet" href="{ASSET_BASE}shared/compara.css?v={VER}">
{{{{ standard_header_includes }}}}
</head>
<body>
{body}
<!-- Lucide con async y version FIJA, no defer ni @latest. Medido: con defer y @latest
     bloqueaba el DOMContentLoaded 4,3s en 3G (defer se ejecuta ANTES del DOMContentLoaded
     por especificacion, y @latest agrega la resolucion de version). El onload crea los
     iconos sin depender de que compara.js todavia no haya corrido. -->
<script async src="https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js"
        onload="window.lucide&&lucide.createIcons({{attrs:{{'stroke-width':1.75}}}})"></script>
<script src="{ASSET_BASE}shared/compara.js?v={VER}" defer></script>
<script>
{redirect_js}
</script>
{{{{ standard_footer_includes }}}}
</body>
</html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    out = build(a.slug)
    if a.out:
        pathlib.Path(a.out).write_text(out, encoding="utf-8")
        print(f"{a.slug}: {len(out)//1024}KB -> {a.out}")
    else:
        sys.stdout.write(out)
