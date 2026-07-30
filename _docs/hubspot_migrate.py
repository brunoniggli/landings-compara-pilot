#!/usr/bin/env python3
"""
Migra una landing del patrón loader+fetch al patrón server-rendered (template codeado).

Qué hace, por landing:
  1. genera el template con _docs/hubspot_template.py
  2. lo crea (POST) o actualiza (PUT) en el portal, en landings-compara/<slug>.html
  3. apunta la página a ese template, limpia el headHtml (saca el loader, deja GTM,
     AB Tasty y el noindex) y vacía el módulo rich_text del cuerpo
  4. push-live

Uso:
    python3 _docs/hubspot_migrate.py salud-complementario

Requiere /tmp/hs-pages.json con el mapa slug -> {id}. Se regenera leyendo las páginas
del portal si hiciera falta.

Ganancia medida en mobile 3G rápido + CPU 4x (antes -> después):
    FCP  1048ms -> 330ms
    LCP  2408ms -> 1634ms
    CLS  0,0075 -> 0,0436   (los dos bien dentro de "bueno", < 0,1)

NO migrar la landing de Auto/CICL: está en un A/B test activo y cambiar el modo de
entrega ensucia la lectura del test.
"""
import json, urllib.request, urllib.error, re, sys, pathlib, subprocess

TOK=[l.split("=",1)[1].strip().strip('"').strip("'") for l in
     open("/Users/brunongiorgini/ClaudeCode/Claudia/.secrets/hubspot.env") if l.startswith("HUBSPOT_TOKEN=")][0]
H={"Authorization":f"Bearer {TOK}","Content-Type":"application/json"}
REPO=pathlib.Path.home()/"ClaudeCode/landings-compara"

def call(m,u,d=None):
    req=urllib.request.Request(u,method=m,headers=H,data=json.dumps(d).encode() if d else None)
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            raw=r.read(); return r.status,(json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:400]

def head_limpio(hh_actual):
    """Deja solo lo que sigue siendo necesario en el headHtml: viewport, AB Tasty, GTM,
       noindex. Fuera: los <link> de CSS y todo el loader (ahora viven en el template)."""
    partes=[]
    partes.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    ab=re.search(r'<script src="https://try\.abtasty\.com/[^"]+"></script>', hh_actual)
    if ab: partes.append("<!-- AB Tasty (sincrono) -->\n"+ab.group(0))
    gtm=re.search(r"<script>\(function\(w,d,s,l,i\).*?GTM-[\w]+'\);</script>", hh_actual, re.S)
    if gtm: partes.append("<!-- Google Tag Manager (dispara Heap) -->\n"+gtm.group(0))
    partes.append('<meta name="robots" content="noindex,nofollow">')
    partes.append("<!-- El HTML, CSS y JS de la landing viven en el template codeado\n"
                  "     (server-rendered). Ya no hay loader ni fetch: no volver a agregarlo. -->")
    return "\n".join(partes)

def migrar(slug, page_id):
    # 1. genera el template desde el .html
    tpl = subprocess.run([sys.executable, str(REPO/"_docs/hubspot_template.py"), slug],
                         capture_output=True, text=True, check=True).stdout
    path=f"landings-compara/{slug}.html"
    # 2. crea o actualiza el template en el portal
    st,b = call("GET", f"https://api.hubapi.com/content/api/v2/templates?path={path}&limit=1")
    existente = (b.get("objects") or [None])[0] if isinstance(b,dict) else None
    if existente:
        st2,b2 = call("PUT", f"https://api.hubapi.com/content/api/v2/templates/{existente['id']}",
                      {"source":tpl, "path":path})
        tid, accion = existente["id"], f"PUT {st2}"
    else:
        st2,b2 = call("POST","https://api.hubapi.com/content/api/v2/templates",
                      {"path":path,"source":tpl,"template_type":4,
                       "is_available_for_new_content":False})
        if st2 not in (200,201): return False, f"template {st2}: {b2}"
        tid, accion = b2["id"], f"POST {st2}"
    # 3. apunta la pagina al template nuevo, limpia headHtml y vacia el modulo del cuerpo
    st3,pg = call("GET", f"https://api.hubapi.com/cms/v3/pages/landing-pages/{page_id}")
    if st3!=200: return False, f"GET page {st3}"
    ls=json.loads(json.dumps(pg["layoutSections"]))
    try: ls["dnd_area"]["rows"][0]["0"]["params"]["html"]=""   # el div ya está en el template
    except Exception: pass
    st4,_ = call("PATCH", f"https://api.hubapi.com/cms/v3/pages/landing-pages/{page_id}/draft",
                 {"templatePath": path, "headHtml": head_limpio(pg.get("headHtml") or ""),
                  "layoutSections": ls})
    st5,_ = call("POST", f"https://api.hubapi.com/cms/v3/pages/landing-pages/{page_id}/draft/push-live")
    ok = st4==200 and st5 in (200,204)
    return ok, f"template {accion} id={tid} | PATCH {st4} | push-live {st5} | {len(tpl)//1024}KB"

if __name__=="__main__":
    slug=sys.argv[1]
    pages=json.load(open("/tmp/hs-pages.json"))
    ok,msg = migrar(slug, pages[slug]["id"])
    print(("OK  " if ok else "FALLO  ")+slug+": "+msg)
