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

Desde 2026-07-30 TODOS los assets (CSS, JS, fuentes woff2, logos, imágenes) viven en el
File Manager de HubSpot, subidos por _docs/hubspot_upload_assets.py. Ya no hay ninguna
dependencia de GitHub Pages ni de un repo personal.

Uso:
    python3 _docs/hubspot_template.py salud-complementario     # imprime el template
    python3 _docs/hubspot_template.py salud-complementario -o /tmp/t.html
"""
import pathlib, re, sys, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Los assets viven en el File Manager de HubSpot. Ventajas sobre GitHub Pages: sale la
# dependencia de un repo personal, y HubSpot los sirve desde el dominio de la página, o sea
# same-origin. El CSS y el JS siguen siendo externos, no inline: inlinearlos empeora el
# DOMContentLoaded 4x y rompe el cache compartido entre las 23 landings.
CDN = "https://22319441.fs1.hubspotusercontent-na1.net/hubfs/22319441/landings-compara/"

# Landings que se apartan del default. Hoy solo Auto/CICL.
#
# Auto nació en el repo de Charlie y su CSS divergió del nuestro en 144 líneas, y no son
# cosméticas: H1 52px contra 44px, columnas 1.05/0.95 contra 1.15/0.85, benefits en grid
# contra flex, orden distinto en mobile. Es la versión que GANÓ el A/B contra la landing
# antigua, así que se sirve con SU hoja: migrar el modo de entrega no debe cambiarle un
# pixel. Las diferencias del nuestro son el feedback de diseño del 29-30/07, validado para
# las landings de New Business y no para Auto. Portarlas es una decisión de negocio con
# medición, no un efecto colateral de una migración de hosting.
#
# OJO: esto va indexado por SLUG, no por "si me pasaron --src". Antes dependía de --src y
# entonces el comando documentado (`hubspot_migrate.py auto`, que no pasa --src) generaba
# la página sin estos overrides y le devolvía el CLS a 0,26.
ESPECIALES = {
    "auto": {
        "css": "compara-auto.css",
        # aspect-ratio: las imágenes venían sin dimensiones declaradas y el reflow al
        # cargar la del hero daba un solo shift de 0,471, con CLS de 0,26. Con esto, 0.
        # animación: se acorta en mobile en vez de quitarse. Quitarla del todo bajaba el
        # LCP a 294ms pero disparaba el CLS a 0,277, porque estaba tapando el shift del
        # font-swap. Acortarla a 420ms deja los dos bien.
        "style": ("@media (max-width:860px){.js .hero-enter{animation-duration:.42s;"
                  "animation-delay:0ms!important}}"
                  ".hero-figure img{aspect-ratio:1459/1347}"
                  ".promo-banner img{aspect-ratio:4001/618}"
                  "@media (max-width:640px){.promo-banner img{aspect-ratio:1668/976}}"),
    },
}

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

def build(slug: str, src_path: pathlib.Path = None) -> str:
    esp  = ESPECIALES.get(slug, {})
    hoja = esp.get("css", "compara.css")
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

    # No hay cache bust: el File Manager sobreescribe el archivo en la misma URL y el
    # template se vuelve a subir en cada migración.
    #
    # OJO: el primer comentario del archivo lo parsea HubSpot como YAML de metadata.
    # Solo claves ahí; cualquier texto libre rompe el POST con "Unable to process
    # annotated template metadata". La documentación va en un segundo comentario.
    override_auto = f'<style>{esp["style"]}</style>' if esp.get("style") else ""

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
<!-- Sin preload de fuentes, a propósito. Se probó con y sin crossorigin y en los dos casos
     el navegador bajaba cada fuente DOS veces (95KB de más en la ruta crítica): el preload
     y la petición que hace el CSS no coinciden en modo de request. Con las fuentes ya en
     woff2 (50KB y 44KB) y servidas same-origin desde el File Manager, el preload aportaba
     poco y costaba el doble de bytes. Medido. -->
{preload_hero}
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="stylesheet" href="{CDN}css/colors_and_type.css">
<link rel="stylesheet" href="{CDN}css/{hoja}">
{override_auto}
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
    a = ap.parse_args()
    out = build(a.slug, pathlib.Path(a.src) if a.src else None)
    if a.out:
        pathlib.Path(a.out).write_text(out, encoding="utf-8")
        print(f"{a.slug}: {len(out)//1024}KB -> {a.out}")
    else:
        sys.stdout.write(out)
