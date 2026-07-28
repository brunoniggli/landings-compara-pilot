# 06 — Glosario

**KV (Key Visual)**
La pieza visual principal de una campaña o marca. En este proyecto, la landing "Home" cumple ese rol: es la vitrina de marca donde conviven todos los productos.

**CICL**
Nombre interno de la campaña/promoción de Seguro de Auto usada como caso de éxito de este proyecto (aparece en el nombre del PDF de condiciones alojado en Cloudinary: `CICL_20dcto_Junio_2026`). Cuando se habla de "la landing CICL" o "el caso CICL", se refiere a `auto.html` — la landing de Seguro de Auto que se aprobó e implementó en HubSpot. **Su significado exacto (sigla de qué) no está confirmado en ninguna sesión disponible** — ver `07_PENDIENTES_Y_NOTAS_TECNICAS.md`.

**Loader (headHtml)**
El script real que hace funcionar la landing dentro de HubSpot: vive en el `headHtml` de la página (no en el módulo del cuerpo, porque HubSpot elimina los `<script>` inline de los módulos `rich_text`) y hace `fetch()` del HTML y del JS de la landing directo desde GitHub Pages, inyectándolos en un contenedor vacío (`#compara-app`) dentro del cuerpo de la página. Ver `04_IMPLEMENTACION_HUBSPOT.md`.

**Opción B**
Alternativa recomendada (y todavía no ejecutada) a la implementación actual en HubSpot: un template custom-coded y server-rendered, subido vía HubSpot CLI, sin el `fetch`/loader asíncrono. Se plantea como necesaria si el equipo requiere tests de AB Tasty por modificación de elementos (no solo split-URL).

**AB Tasty / Heap / GTM**
Herramientas de testing y analítica agregadas al `headHtml` de la landing en HubSpot (no viven en el código fuente de `source/`): AB Tasty corre los tests A/B, GTM (`GTM-8GLF`) dispara Heap para analítica de comportamiento. Ninguna de las tres está documentada en el HTML fuente de este paquete — se agregan solo al momento de publicar en HubSpot.

**Landing puente ("bridge landing")**
Patrón de landing de un solo producto y un solo objetivo de conversión (cotizar), sin navegación ni CTAs que compitan con ese objetivo. Es el patrón de `auto.html` y el que debe seguir cualquier landing de producto nueva (a diferencia de "Home", que es multi-producto).

**Home**
La landing de marca (`index.html`): vitrina con todos los productos, hero con selector de qué cotizar, demo de chat con "Compa", carrusel de productos. Sirve como referencia visual y como punto de entrada que enlaza a cada landing de producto.

**data-cotiza**
Atributo HTML usado en todos los botones de cotización de una landing de producto. Un script central (al final de cada archivo `.html`) detecta todos los elementos con este atributo y les inyecta la URL real del formulario de cotización, preservando `gclid` y `utm_*` del clic original.

**Compa**
El personaje/avatar de marca de Compara. Aparece como logo alternativo en el nav en mobile (`bc-compa-feliz.svg`) y como el "asesor" que conversa en la demo de chat de Home.

**FORM (variable del script)**
Variable al final de cada landing de producto (`auto.html`, y cualquier landing nueva) que define la URL real del formulario de cotización de ese producto. Mientras valga `'#'`, todos los botones `[data-cotiza]` quedan inertes (placeholder) — es el estado esperado hasta que se confirme la URL real.

**design-system (o "brand/design-system")**
Carpeta con todo lo que es de marca y se reutiliza en cualquier landing: paleta de colores y tipografía (`colors_and_type.css`), logos de aseguradoras, íconos de producto, y las fuentes auto-alojadas (Poppins, Open Sans, DM Serif Display).

**shared (o "shared/")**
Carpeta con `compara.css` y `compara.js`: el comportamiento y estilo base que comparten todas las landings del proyecto (nav, animaciones al hacer scroll, CTA sticky, carrusel de productos, marquee de aseguradoras, etc.).
