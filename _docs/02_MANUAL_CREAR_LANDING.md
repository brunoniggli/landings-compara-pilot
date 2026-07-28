# 02 — Manual: cómo crear una landing de producto nueva

Este es el procedimiento técnico completo, en el mismo orden en que conviene ejecutarlo. Asume que ya se completó el checklist de `01_REQUISITOS_PARA_LANDING_NUEVA.md`.

## Paso 1 — Duplicar la plantilla

Copia `templates/template-landing-producto.html` (no `source/auto.html` directamente, aunque son equivalentes — la plantilla ya trae los placeholders marcados) a `source/[producto].html`.

Convención de nombres: minúsculas, sin tildes ni espacios, palabra única si es posible (`vida.html`, `salud.html`, `viaje.html`, `soap.html`).

## Paso 2 — Reemplazar el contenido de marca/producto

En el nuevo archivo, reemplaza todos los placeholders `{{ASI}}` que trae la plantilla (están comentados junto a cada uno). En orden de aparición en el archivo:

1. `<title>` y `<meta name="description">`
2. Título del hero (`<h1>`) y bajada (`hero-sub`)
3. Texto del botón de CTA del hero (aparece repetido: hero, banner si existe, CTA final, y sticky mobile — **debe ser idéntico en las 4 apariciones**, es el mismo mensaje de conversión repetido a propósito)
4. Los 3 puntos de confianza (`hero-trust`)
5. Bloque de banner promocional: si el producto **no** tiene promoción activa, **elimina toda la sección** `<!-- BANNER PROMOCIONAL -->` completa, no la dejes vacía o rota
6. Sección de aseguradoras: reemplaza el listado de `logo-capsule` por las aseguradoras que correspondan a ese producto (usa los logos ya existentes en `brand/design-system/assets/logo_*.svg`; si falta un logo, es parte del checklist de requisitos, no se inventa)
7. Sección "cómo funciona": los 3 pasos
8. Sección de coberturas/beneficios: los 3-4 bloques, cada uno con su ícono (reutiliza `small_icon_*.svg` existentes cuando el concepto calce — ej. `small_icon_users.svg` para "terceros", `small_icon_headset.svg` para "asistencia")
9. CTA final (editorial + título + botón)
10. Al final del archivo, el script de redirección: reemplaza `FORM = '#'` por la URL real del formulario de ese producto

## Paso 3 — Assets

Sube las imágenes específicas de esta landing a `source/assets/`, siguiendo la convención de nombres ya usada en Auto:

- `promo-[producto]-hero.png` (y `-mobile.png` si aplica)
- `promo-[producto]-banner-desktop.png` / `promo-[producto]-banner-mobile.png` (solo si hay promoción)

No dupliques assets de marca (logos, íconos de producto, fuentes) — esos ya viven en `brand/design-system/assets/` y `brand/design-system/fonts/`, y se referencian desde ahí con rutas relativas (`brand/design-system/assets/...`).

## Paso 4 — Enlazar desde Home

En `source/index.html`, agrega la landing nueva en dos lugares:

1. La lista de botones de producto del hero (`hero-products`, clase `hp-btn`) — copia el patrón del botón de Auto y cambia el `href` al nuevo archivo y el ícono
2. La tarjeta del carrusel de productos (`.pcard`, dentro de `#htrack`) — copia el patrón de la tarjeta de Auto, cambia `href`, ícono, título y descripción

Si el producto nuevo tenía antes un placeholder `href="#"` en Home (SOAP, Vida, Salud y Viaje ya están listados como placeholders en el Home actual), simplemente actualiza ese `href="#"` al archivo real en vez de duplicar el bloque.

## Paso 5 — Qué NO tocar (contrato con `compara.js`)

`shared/compara.js` engancha su comportamiento a IDs y clases específicas. Si tu HTML nuevo usa alguno de estos elementos, **respeta el nombre exacto** (compara.js no hace nada si el elemento no existe, así que omitir una sección es seguro — lo que no es seguro es usar un nombre distinto para la misma función):

| Elemento / selector | Qué activa |
|---|---|
| `#nav`, `#burger`, `#navPanel` | Nav sólido al hacer scroll + menú mobile |
| `#hero`, `#heroGlow` | Luz que sigue al cursor (solo desktop) + pulso al hacer click/tap |
| `.hp-btn` (dentro de `#hero`) | Estado activo al clickear un botón de producto placeholder (`href="#"`) |
| `#productos`, `#hwrap`, `#htrack` | Carrusel de productos que sigue al cursor (solo desktop) |
| `#logoCloud` | Marquee (loop infinito) de logos de aseguradoras en mobile |
| `#chat`, `#chatBody` | Demo de conversación con "Compa" (solo úsalo si la landing lo necesita — Auto no lo tiene) |
| `.cta-sticky` | CTA fijo inferior en mobile, aparece/desaparece según scroll |
| `[data-cotiza]` | Cualquier botón con este atributo recibe automáticamente la URL real del formulario + `gclid`/`utm` preservados |

**No es necesario incluir todas las secciones de Home o de Auto.** Cada landing de producto puede tener menos secciones (por ejemplo, sin demo de chat) y el JS compartido no se rompe — así está diseñado a propósito (ver el comentario al inicio de `compara.js`).

## Paso 6 — Probar

Abre el archivo `.html` nuevo directo en el navegador (doble clic, sin servidor). Revisa:

- Que todos los CTA con `data-cotiza` naveguen a la URL correcta (si ya se cargó la URL real del formulario)
- Que el nav funcione en mobile (probar en un viewport angosto, <861px, o con las devtools)
- Que el CTA sticky aparezca/desaparezca correctamente al scrollear (solo visible en mobile)
- Que ninguna imagen salga rota (revisa la consola del navegador)

Cuando esté aprobado visualmente, continúa con `03_GITHUB_Y_PUBLICACION.md`.
