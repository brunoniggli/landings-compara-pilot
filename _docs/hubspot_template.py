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
ASSET_BASE_DEFAULT = "https://brunoniggli.github.io/landings-compara-pilot/"
# La landing de Auto/CICL vive en el repo de Charlie y su CSS divergió 132 líneas del
# nuestro. Es la versión que ganó el A/B, así que se sirve con SUS assets: migrar el modo
# de entrega no debe cambiarle un pixel.
ASSET_BASE_POR_SLUG = {"auto": "https://cperez-brand.github.io/landings-compara/"}
ASSET_BASE = ASSET_BASE_DEFAULT   # se reasigna en build() según el slug

# Desde 2026-07-30 los assets viven en el File Manager de HubSpot, no en GitHub Pages.
# Ventajas: sale la dependencia de un repo personal y el CDN de HubSpot es más rápido (la
# diferencia de LCP que quedaba en Auto era exactamente eso). El CSS y el JS siguen siendo
# externos, no inline: inlinearlos empeora el DOMContentLoaded 4x y rompe el cache
# compartido entre las 23 landings.
CDN = "https://22319441.fs1.hubspotusercontent-na1.net/hubfs/22319441/landings-compara/"

def a_cdn(ruta: str) -> str:
    """brand/design-system/assets/logo_X.svg -> {CDN}img/logo_X.svg (el File Manager es plano)."""
    nombre = ruta.rsplit("/", 1)[-1]
    if nombre.endswith(".woff2"): return CDN + "fonts/" + nombre
    if nombre.endswith((".css",)): return CDN + "css/" + nombre
    if nombre.endswith((".js",)):  return CDN + "js/" + nombre
    return CDN + "img/" + nombre

def absolutizar(txt: str) -> str:
    """Rutas relativas de assets -> URLs del File Manager."""
    txt = re.sub(r'(src|href|srcset)="((?:brand/|assets/)[^"]+)"',
                 lambda m: f'{m.group(1)}="{a_cdn(m.group(2))}"', txt)
    # Imágenes de Auto: los PNG del repo de origen pesan 3,86MB juntos (el del hero solo,
    # 1,5MB = 7,7s de descarga en 3G). Las webp del nuestro pesan 385KB en total,
    # redimensionadas a 2x del tamaño de exhibición. Se sustituyen por nombre.
    for png in ("promo-auto-hero.png","promo-auto-hero-mobile.png",
                "promo-auto-banner-desktop.png","promo-auto-banner-mobile.png"):
        txt = txt.replace(a_cdn(png), a_cdn(png.replace(".png",".webp")))
    return txt

def css_con_fuentes_absolutas() -> str:
    """colors_and_type.css usa ./fonts/... — hay que reescribirlo al CDN."""
    css = (ROOT/"brand/design-system/colors_and_type.css").read_text(encoding="utf-8")
    return css.replace('url("./fonts/', f'url("{ASSET_BASE}brand/design-system/fonts/')

def build(slug: str, src_path: pathlib.Path = None, asset_base: str = None) -> str:
    global ASSET_BASE
    ASSET_BASE = asset_base or ASSET_BASE_POR_SLUG.get(slug, ASSET_BASE_DEFAULT)
    # Las woff2 solo existen en nuestro repo, así que el preload apunta siempre ahí, incluso
    # cuando el resto de los assets viene de otro CDN (caso Auto, repo de Charlie).
    FONT_BASE = ASSET_BASE_DEFAULT
    src = (src_path or (ROOT/f"{slug}.html")).read_text(encoding="utf-8")

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

    # La imagen del hero es el elemento de LCP: se le da prioridad alta y se precarga.
    # Todo lo que está bajo el pliegue (logos de aseguradoras, banner, iconos de coberturas)
    # pasa a lazy, para que no compita por ancho de banda con el hero.
    # Medido antes de esto: la imagen del hero terminaba de pintar a los 4788ms porque salía
    # última en la cola de descarga, detrás de 10 SVG de logos y el banner.
    hero_img = re.search(r'<img src="([^"]*(?:hero|promo)[^"]*)"', body)
    if hero_img:
        body = body.replace(hero_img.group(0),
            hero_img.group(0).replace("<img ", '<img fetchpriority="high" decoding="async" ', 1), 1)
    # lazy en todo <img> que no sea el del hero ni el logo del nav
    def lazy(m):
        tag = m.group(0)
        if any(k in tag for k in ("fetchpriority", "logo-white", "logo-blue", "logo-compa")):
            return tag
        return tag.replace("<img ", '<img loading="lazy" decoding="async" ', 1)
    body = re.sub(r'<img [^>]*>', lazy, body)

    # preload de la imagen del hero (el elemento de LCP)
    _h = re.search(r'<img[^>]*src="([^"]*(?:hero|promo)[^"]*)"', body)
    preload_hero = (f'<link rel="preload" as="image" href="{_h.group(1)}" fetchpriority="high">'
                    if _h else "")

    if src_path:   # fuente externa (Auto): sin cache bust, el repo de origen no es nuestro
        VER = "external"
    else:
        VER = re.search(r'VER = "([^"]+)"', (ROOT/"_docs/generate.py").read_text()).group(1)

    # OJO: el primer comentario del archivo lo parsea HubSpot como YAML de metadata.
    # Solo claves ahí; cualquier texto libre rompe el POST con "Unable to process
    # annotated template metadata". La documentación va en un segundo comentario.
    # Si el CSS viene de otro CDN, ese CSS todavía pide .ttf. Redefinimos los @font-face
    # apuntando a nuestras woff2 (mismas familias y pesos, solo cambia el formato, así que
    # no cambia nada visual). Va DESPUÉS del <link>, por eso gana.
    # El CSS ya es el nuestro y vive en el CDN, con las @font-face apuntando al File
    # Manager, así que no hace falta override de fuentes. Solo queda el ajuste de mobile.
    override_woff2 = ('<style>@media (max-width:860px){.js .hero-enter{animation-duration:.42s;'
                      'animation-delay:0ms!important}}'
                      '.hero-figure img{aspect-ratio:1459/1347}'
                      '.promo-banner img{aspect-ratio:4001/618}'
                      '@media (max-width:640px){.promo-banner img{aspect-ratio:1668/976}}</style>'
                      if src_path else "")

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
<link rel="icon" href="{CDN}img/avatar_favicon.svg">
<!-- Preload de las 2 fuentes del hero (h1 en Poppins 600, bajada en Open Sans 400).
     En woff2: pesan 50KB y 44KB, contra 152KB y 95KB del .ttf original (62% menos en
     total, de 1,68MB a 638KB las 14). Sin esto el texto del hero re-pinta cuando llega la
     fuente real y el LCP se dispara a ~2,9s en mobile 3G.
     SIN crossorigin a propósito: los assets viven en el File Manager y HubSpot los sirve
     desde el dominio de la página, o sea same-origin. Con crossorigin el preload pide en
     modo CORS y el CSS en modo same-origin, no coinciden, y el navegador baja cada fuente
     DOS veces (95KB de más en la ruta crítica). Medido. -->
<!-- Sin preload de fuentes, a propósito. Se probó con y sin crossorigin y en los dos casos
     el navegador bajaba cada fuente DOS veces (95KB de más en la ruta crítica): el preload
     y la petición que hace el CSS no coinciden en modo de request. Con las fuentes ya en
     woff2 (50KB y 44KB) y servidas same-origin desde el File Manager, el preload aportaba
     poco y costaba el doble de bytes. Medido. -->
{preload_hero}
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="stylesheet" href="{CDN}css/colors_and_type.css">
<link rel="stylesheet" href="{CDN}css/compara.css">
{override_woff2}
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
<script src="{CDN}js/compara.js" defer></script>
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
    ap.add_argument("--src", help="archivo .html de origen si no está en el repo")
    ap.add_argument("--asset-base", help="CDN de los assets si no es el nuestro")
    a = ap.parse_args()
    out = build(a.slug, pathlib.Path(a.src) if a.src else None, a.asset_base)
    if a.out:
        pathlib.Path(a.out).write_text(out, encoding="utf-8")
        print(f"{a.slug}: {len(out)//1024}KB -> {a.out}")
    else:
        sys.stdout.write(out)
