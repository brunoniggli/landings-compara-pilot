# 05 — Aprendizajes reales del caso Auto/CICL

Este documento resume, en orden cronológico, los ajustes reales que se hicieron a la landing de Seguro de Auto desde su primera versión hasta la que se aprobó e implementó en HubSpot. Vale la pena leerlo completo antes de crear una landing nueva: varias de estas vueltas ya están resueltas y no hace falta repetirlas.

**Nota de procedencia:** los puntos 1 a 6 están construidos directamente del historial de commits de GitHub (verificables en el código). Los puntos 7 y 8 vienen del relato de la sesión de Claude Code donde se implementó la landing en HubSpot — son reales y de primera mano, pero no verificables directamente desde el repositorio, así que se marcan explícitamente dónde hay datos concretos y dónde solo hay una descripción cualitativa.

## 1. Colores de hover no son uniformes entre botones
Se definió que cada tipo de botón tiene su propio color de hover: el CTA primario (`.btn--primary`, fondo azul marca) usa `#4168FF` al hacer hover; el CTA sobre fondo oscuro del hero (`.btn--white`) usa `#779BFF`. **No asumir el mismo color de hover para todos los CTA de una landing** — depende del fondo sobre el que está el botón.

## 2. Ronda de feedback grande: se revisan Home y producto juntos
El feedback de negocio llegó agrupado, tocando nav, contenido, aseguradoras, coberturas, copy y espaciados de **ambas** landings a la vez (no landing por landing). Aprendizaje de proceso: conviene juntar el feedback de Home y de la landing de producto en la misma pasada de revisión, porque suelen afectarse mutuamente (ej. quitar la sección de aseguradoras de Home porque ya está en el producto).

De esa ronda salieron cambios permanentes:
- El logo del nav cambia a un avatar más pequeño al hacer scroll
- El chat demo de Home se rediseñó (texto plano, píldoras, nuevo input, personaje "Compa")
- La sección de aseguradoras se sacó de Home (queda solo en la landing de cada producto)
- El copy se unificó en "5 minutos" como tiempo estimado de cotización en todas las landings

## 3. Patrón "landing puente": un solo objetivo de conversión
Este es el aprendizaje más importante para replicar en landings nuevas. Una landing de producto (a diferencia de Home) debe tener **un solo objetivo**: que la persona cotice. Por eso:
- El CTA de navegación que compite con la conversión ("Conversemos de seguros") se **oculta**, no se borra — queda comentado en el HTML por si se necesita reactivar a futuro
- El logo del nav deja de anclar a secciones internas y enlaza directo al sitio corporativo (`comparaonline.cl`)
- El mensaje de confianza pasa de un número específico ("+15 aseguradoras") a una afirmación más fuerte y sin fecha de vencimiento ("Todas las aseguradoras") — evita que el copy quede desactualizado si el número de aseguradoras cambia

## 4. Jerarquía visual en mobile: la oferta primero
En mobile, la imagen promocional (que trae el cartel de descuento) se reordena para aparecer **antes** que el título y el copy — la oferta es lo primero que se ve, no el texto. También se probó agrandar el logo estático del nav (+20%) y bajar la altura del hero para que el banner promocional se alcance a insinuar sin necesidad de hacer scroll.

## 5. A/B test: el botón real le ganó al botón dibujado en la imagen
Se probó una versión donde el botón "Cotiza" venía dibujado dentro de la imagen promocional (toda la imagen era clickeable). Un test A/B mostró que esa versión **rendía peor** que la alternativa: imagen promocional limpia arriba + un botón HTML real debajo, ambos apuntando al mismo formulario. Se revirtió a la segunda opción.

**Aprendizaje para futuras landings:** no asumir que integrar el CTA dentro de una imagen se ve "más pulido" y por eso convierte mejor — un botón real de HTML (accesible, con foco de teclado, sin depender de que el usuario acierte el pixel exacto sobre una imagen) puede rendir mejor. Si hay dudas de este tipo, vale la pena replicar el test A/B en vez de asumir el resultado de Auto como universal.

## 6. CTA sticky en mobile: aparece y desaparece con propósito
La versión final agrega un CTA fijo abajo, solo visible en mobile, que:
- Aparece quando el usuario se aleja del CTA del hero (deja de estar en pantalla)
- Desaparece de nuevo al llegar al CTA final de la página (para no duplicar visualmente el mismo mensaje dos veces en la misma vista)
- Usa exactamente la misma URL/lógica de redirección que los demás botones de cotización

## 7. El A/B test del CTA-en-imagen: lo que sí se sabe y lo que no

El punto 5 de más arriba ya contaba que el botón "dibujado dentro de la imagen" se revirtió por rendir peor. Esto es lo que se pudo reconstruir de esa decisión desde la sesión de implementación en HubSpot:

- **No hay cifras concretas documentadas** (tasas de conversión, tamaño de muestra). Lo único que se comunicó fue cualitativo: "tanto AB Tasty como Heap muestran que la nueva landing performa peor que la antigua".
- **Hipótesis de subconteo, no descartada:** si el evento de clic en Heap/AB Tasty estaba definido por selector o texto del botón real, los taps sobre la imagen (mientras el CTA vivió ahí) probablemente **no se contaban como clic**. Es posible que parte de la caída medida sea un problema de medición, no de comportamiento real de las personas. Esto no se confirmó ni se descartó — queda como duda abierta.
- **Un factor aparte del diseño puede estar pesando:** esta landing en HubSpot carga su contenido vía `fetch()` en el navegador de la persona (con un retraso de ~200-400ms tras la carga inicial de la página), mientras que la landing anterior era renderizada directo por el servidor. Ese retraso podría afectar el rendimiento en mobile/SEM **independientemente** de qué diseño de CTA se use — es otra variable que se mezcla con el resultado del test.

**Para una landing nueva:** si se repite un test de este tipo, vale la pena confirmar primero que el tracking cuenta clics sobre imágenes igual que sobre botones reales, y tener en cuenta que la forma en que se implementó en HubSpot (ver `04_IMPLEMENTACION_HUBSPOT.md`) puede introducir su propio ruido de performance, separado del diseño que se está probando.

## 8. Caminos técnicos descartados al implementar en HubSpot (no repetir la vuelta)

Estos no están en los commits de GitHub porque ocurrieron del lado de HubSpot, no del código fuente:

- Crear la página vía `CREATE_FROM_TEMPLATE` del conector de HubSpot falló con **todas** las plantillas probadas — se abandonó ese camino completo (detalle en `04_IMPLEMENTACION_HUBSPOT.md`).
- Insertar el HTML como módulo `@hubspot/html` no funciona en este portal (no existe como built-in) — hay que usar `@hubspot/rich_text` con un contenedor vacío y el loader real en el `headHtml`.
- Resetear el CSS del tema de HubSpot de forma agresiva (apuntando a los wrappers globales del tema) rompió la página por completo (quedó en blanco) — cualquier override de estilos debe acotarse solo al contenedor de la landing, nunca a elementos globales del tema.

## 9. Detalles técnicos que vale la pena mantener en landings nuevas

- **Atribución de tráfico pagado:** el script de redirección preserva `gclid` y los parámetros `utm_*` del clic original al armar la URL final del formulario. Sin esto se pierde atribución de campañas pagadas — no es opcional para una landing con tráfico SEM.
- **Un solo atributo para todos los CTA de conversión:** todos los botones que deben ir al formulario usan `[data-cotiza]` en vez de IDs individuales. Un solo script central los detecta a todos y les inyecta la URL real — agregar un CTA nuevo en una landing futura es tan simple como agregarle ese atributo.
- **JS modular y defensivo:** cada bloque de `compara.js` revisa primero si su elemento existe en el HTML antes de activarse. Esto permite que una landing más simple (sin chat demo, sin carrusel) no rompa nada aunque no incluya esas secciones — es un patrón a mantener, no a "arreglar".
- **Placeholders explícitos, nunca silenciosos:** cuando un asset o una URL real todavía no estaba lista (la banda fotográfica de Home, el banner promocional de Auto, la URL del formulario), se dejó un comentario `TODO` explícito en el código y/o un valor placeholder (`FORM = '#'`) en vez de dejarlo vacío o inventar un valor. Esto permite lanzar el resto de la landing sin bloquear todo el trabajo por una pieza pendiente — y es exactamente la práctica que debe seguir Claude Code cuando falte algo del checklist de requisitos.
