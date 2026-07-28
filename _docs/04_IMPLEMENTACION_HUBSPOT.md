# 04 — De prototipo a página real en HubSpot

Esta versión reemplaza una anterior que era una recomendación genérica. Lo de abajo es el **proceso real** usado para publicar la landing de Seguro de Auto (CICL) en HubSpot, reconstruido a partir de la sesión de Claude Code donde se hizo el trabajo. Se marca explícitamente qué quedó confirmado y qué quedó pendiente/abierto al cierre de esa sesión.

## El enfoque real: no fue plantilla codeada, fue un "loader" en el head

A diferencia de lo que suele recomendarse por defecto (Design Manager con plantilla codeada), en este caso se usó un camino distinto, por dos limitaciones concretas de este portal de HubSpot:

- El tipo de módulo `@hubspot/html` **no existe** como built-in en este portal.
- El módulo `@hubspot/rich_text` (que sí existe) **elimina las etiquetas `<script>` inline** al renderizar — un script puesto directamente dentro del módulo simplemente no corre.

Por eso el patrón final quedó así:

1. En el **cuerpo de la página** (vía el módulo `@hubspot/rich_text`, insertado con el conector MCP de HubSpot) solo vive un contenedor vacío: `<div id="compara-app">`.
2. La lógica real — el "loader" que trae el HTML y lo inyecta en ese div — vive en el **`headHtml` de la página** (seteado vía `SET_METADATA`), porque ahí los scripts sí ejecutan (igual que corren GTM o AB Tasty).
3. El loader hace `fetch()` de `auto.html` y de `compara.js` directamente desde GitHub Pages en tiempo real. `colors_and_type.css` y `compara.css` se enlazan con `<link>` normal, también apuntando a GitHub Pages.

**Ninguno de los archivos (CSS, JS, fuentes, imágenes) se subió al File Manager de HubSpot.** Todo queda enlazado a `https://cperez-brand.github.io/landings-compara/` como CDN.

### La consecuencia importante de esto (para bien y para mal)

- **A favor:** hacer `push` a GitHub actualiza la landing de HubSpot sola — no hace falta volver a tocar HubSpot para publicar un cambio de copy o diseño.
- **En contra:** HubSpot depende al 100% de que GitHub Pages esté arriba. Si el repo se cae, se pone privado, o Pages se desactiva, la landing en HubSpot deja de funcionar aunque HubSpot mismo esté perfecto.

## Estado de la página en HubSpot (al cierre de la sesión donde se hizo esto)

| Dato | Valor |
|---|---|
| Content ID | `216684642329` |
| Nombre interno | "Comparini - Auto (test AB)" |
| Slug | `comparini-compara-new` |
| Tema | `@hubspot/elevate` |
| Estado | **Borrador** — no confirmado como publicada al cierre de la sesión |
| Dominio deseado | `seguro.comparaonline.cl` |
| Dominio real usado durante el preview | `segurovida.comparaonline.cl` — **marcado como incorrecto** (es el dominio de la landing de Vida, no de Auto) |

**Pendiente sin resolver al cierre de esa sesión:** corregir el dominio a `seguro.comparaonline.cl` y publicar. Carlos tomó esa tarea para sí mismo ("puedo ver tanto el dominio como publicar yo mismo") — **no está confirmado en esta documentación si ya se hizo.** Antes de asumir que la landing está publicada y en el dominio correcto, hay que verificarlo directamente en HubSpot.

## Formulario y tracking

- **Formulario:** se mantuvo la redirección externa (no el formulario nativo de HubSpot). La variable `FORM` del script apunta a `https://seguro-auto.comparaonline.cl/quote`, preservando `gclid`/`utm_*` — mismo patrón que en el archivo fuente.
- **Tracking agregado en el `headHtml`:**
  - AB Tasty (script síncrono: `https://try.abtasty.com/652ee3c0292f98a9efc5c92f31ef39cd.js`)
  - GTM `GTM-8GLF`, que a su vez dispara Heap (confirmado por el equipo de IT del lado de Carlos)
  - `<meta name="robots" content="noindex,nofollow">`

## Accesos usados

- Conector MCP de HubSpot conectado a la cuenta de Carlos, con permiso `LANDING_PAGE` de lectura y escritura.
- No quedó documentado qué rol específico de HubSpot (Marketing Hub, etc.) tiene Carlos — solo que su cuenta tenía permisos suficientes para crear/editar landing pages.
- Si el equipo decide pasar a la "Opción B" (más abajo), se necesita además una **Personal Access Key de HubSpot** — se pidió pero no se llegó a usar en esta sesión.

## Caminos que se probaron y se descartaron (no repetir)

- **`CREATE_FROM_TEMPLATE` vía el conector de HubSpot falló con todas las plantillas probadas** (`@hubspot/growth`, `@hubspot/elevate`, un id real "GiantFocal", e `id:-1`) — siempre con error "Unknown RPC service error". Se abandonó ese camino completo.
  **Workaround que sí funcionó:** Carlos crea la página en blanco desde la interfaz de HubSpot, y desde ahí se completa por conector.
- Se intentó insertar el HTML como módulo `@hubspot/html` — rechazado por no ser un built-in reconocido en este portal (ver arriba).
- Se intentaron resets agresivos de CSS contra los wrappers del tema Elevate en el `headHtml` (`body main{...}`, `body .body-wrapper>*{...}`) para forzar que la landing ocupe todo el ancho — esto dejó la página **completamente en blanco** en el preview real. Se revirtió a overrides con alcance acotado solo a `#compara-app`.

## "Opción B" — el camino recomendado si esto deja de ser suficiente

Esta implementación en HubSpot es **explícitamente un puente/test**, no el camino de producción limpio. Si el equipo necesita un test de AB Tasty por **modificación de elementos** (no solo split-URL/redirect — ver el riesgo explicado en `05_APRENDIZAJES_CASO_CICL.md`), el camino recomendado y **nunca ejecutado todavía** es:

- Subir un template custom-coded, **server-rendered** (sin `fetch`/async), vía HubSpot CLI (`npx @hubspot/cli`), 1:1 con el HTML fuente, con AB Tasty cargado directo en el `<head>`.

Esto requiere la Personal Access Key mencionada arriba y quedó solo planteado, no ejecutado.

## Un dato de seguridad para replicar (protocolo de token de GitHub)

En un momento de esta sesión, el conector de GitHub disponible era de solo lectura. La publicación real a GitHub Pages se hizo con `git` + un **token de acceso personal de GitHub de un solo uso**, que Carlos pegaba en el chat cada vez que había que hacer un deploy. El protocolo seguido (y que conviene mantener con el equipo nuevo):

1. Clonar el repo con el token
2. Hacer el push
3. Borrar el clon local
4. Verificar que no quedaran rastros del token en disco
5. Recordarle a quien lo generó que lo revoque en GitHub inmediatamente después

## Puntos que siguen sin confirmar (no asumir)

- [ ] Si la página ya se publicó y en qué dominio quedó realmente
- [ ] Rol/plan exacto de HubSpot con el que se trabajó
- [ ] Si el equipo decidió que se necesita la "Opción B"
- [ ] Si la cuenta de Cloudinary donde vive el PDF de condiciones es de uso general del equipo o específica de esta campaña (ver `07_PENDIENTES_Y_NOTAS_TECNICAS.md`)

## Para más detalle técnico línea por línea

Los selectores CSS exactos, el comportamiento completo del loader, y el detalle del `contentId` viven en el memory file `project-hubspot-landing.md` de la sesión de Claude Code original — si quien recibe este traspaso tiene acceso a esa sesión, ese archivo tiene el nivel más granular, más allá de este resumen.
