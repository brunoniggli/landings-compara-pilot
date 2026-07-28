# landings-compara

Landings de producto de Compara. HTML estático, sin build, sin frameworks: cada `.html` se abre
directo en el navegador y se sirve tal cual desde GitHub Pages, que es el CDN que consume HubSpot.

Origen: traspaso de Carlos Perez (28/07/2026), `cperez-brand/landings-compara`. Este repo es la
versión de la organización — es el que debe ser fuente de verdad de producción, para que las
landings no dependan de una cuenta personal.

## Landings

| Archivo | Producto | BU | Estado |
|---|---|---|---|
| `index.html` | Home / vitrina de marca (KV) | — | Referencia visual. No es plantilla a clonar |
| `auto.html` | Seguro de Auto | CICL | Aprobada e implementada en HubSpot |
| `salud.html` | Seguro Complementario de Salud | HICL | **Borrador** — pendientes en `_docs/BRIEF-HICL-SALUD.md` |

## Estructura

```
index.html, auto.html, salud.html   ← una landing por producto
assets/                             ← imágenes específicas de UNA landing
brand/design-system/                ← marca: colores, tipografía, logos de cías, íconos, fuentes
shared/                             ← compara.css + compara.js, compartidos por TODAS las landings
_docs/                              ← manual, brief por landing, plantilla, previews
```

`shared/` y `brand/` no se tocan al crear una landing nueva. Si necesitas un comportamiento nuevo,
se agrega en `compara.js` manteniendo el patrón: cada módulo se autoactiva solo si su elemento
existe en el HTML, así una landing simple no rompe.

## Crear una landing nueva

1. Llenar el brief (`_docs/01_REQUISITOS_PARA_LANDING_NUEVA.md`, o copiar el formato de `_docs/BRIEF-HICL-SALUD.md`)
2. Copiar `_docs/template-landing-producto.html` a `<producto>.html`
3. Seguir `_docs/02_MANUAL_CREAR_LANDING.md`
4. Enlazar desde `index.html` (botón del hero + tarjeta del carrusel)
5. Probar: abrir el `.html`, revisar consola, mobile <861px, CTA sticky
6. Publicar: `_docs/03_GITHUB_Y_PUBLICACION.md` → `_docs/04_IMPLEMENTACION_HUBSPOT.md`

Lee `_docs/05_APRENDIZAJES_CASO_CICL.md` antes de empezar. Varias vueltas ya están resueltas
(el A/B del CTA dentro de la imagen, el patrón "landing puente", el copy que no caduca).

## Reglas que no se rompen

- **No inventar** copys, precios, coberturas, nombres de aseguradoras ni URLs de formularios.
  Si falta un dato, va un placeholder visible + `TODO`, nunca un valor inventado.
- El texto del CTA se repite **idéntico** en todas sus apariciones de una misma landing.
- Todo CTA de conversión usa `[data-cotiza]`. El script central le inyecta la URL del formulario
  preservando `gclid` y `utm_*` — sin eso se pierde atribución de paid.
- Una landing de producto tiene **un solo objetivo de conversión** (patrón "landing puente"): sin
  navegación que compita, sin CTA alternativo.
- No duplicar `shared/` ni `brand/` por landing.
- Sin promoción vigente → se borra la sección del banner completa, no se deja vacía.

## Convención de commits

Prefijo con la landing afectada, minúsculas, sin punto final. Si el cambio es solo mobile, va
entre paréntesis:

```
salud: coberturas reales y logo de Alemana
auto (mobile): separar CTA de la imagen
ambas: unifica el copy de tiempo de cotización
```

## Cuidado con esto

La implementación actual en HubSpot **no** es un template codeado: es un `<div id="compara-app">`
vacío en el cuerpo + un loader en el `headHtml` que hace `fetch()` de este repo vía GitHub Pages.

- A favor: un `push` acá actualiza la landing en HubSpot sin tocar HubSpot.
- En contra: si Pages se cae o el repo se pone privado, la landing deja de renderizar. Y el
  contenido llega con 200-400ms de retraso, lo que puede afectar performance en mobile/SEM y
  rompe los tests de AB Tasty por modificación de elemento (usar split-URL).

Detalle completo y el camino recomendado a futuro ("Opción B": template server-rendered vía
HubSpot CLI) en `_docs/04_IMPLEMENTACION_HUBSPOT.md`.
