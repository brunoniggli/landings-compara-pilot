# Brief — Landing Seguro Complementario de Salud (HICL)

Para: Aroldo · Estado: pendiente de llenar · Landing borrador: `salud.html`

Esto es el checklist de `01_REQUISITOS_PARA_LANDING_NUEVA.md` convertido en formulario.
La landing borrador ya existe con la forma armada — lo que falta es reemplazar los
`[TODO AROLDO]` con contenido real. **No inventamos nada**: cada campo vacío acá es un
placeholder visible en la página.

Los campos marcados **BLOQUEANTE** impiden publicar. El resto deja la landing publicable
pero incompleta.

---

## 0. Decisiones (esto no es detalle, define el mensaje)

### 0.1 Denominación del producto
El sitio usa "Seguro de Salud" (`comparaonline.cl/seguro-de-salud`), pero los search terms
que dan señal en la cuenta son de "seguro complementario" (`seguro complementario de salud
consorcio`, `seguro complementario consorcio`). El borrador usa "Seguro Complementario de
Salud" en el `<h1>` y "Seguro de Salud" en el CTA.

- [ ] Confirmar o cambiar: ______________________

### 0.2 Ángulo del hero — RESUELTO 2026-07-28
El hero usa el mismo eje que Auto: *"Tu Seguro Complementario de Salud, al mejor precio"*.
El funil de cotización de Salud sí muestra precios, así que la promesa es sostenible
(confirmado por Bruno). Una versión anterior de este brief decía lo contrario por confundir
contextos: lo que no trae precio en Salud es el **requote de presales/CRM** (templates de
WhatsApp), no el funil web.

- [ ] Aroldo valida el copy final del hero: ______________________

### 0.3 Cierre: ¿100% online o asistido? — BLOQUEANTE
Auto dice *"Contrata 100% online: eliges, pagas y tu póliza llega a tu correo"*. En Salud hay
presales por CRM activo, así que **no afirmamos autoservicio sin confirmarlo**. Si el cierre
es asistido por un ejecutivo, eso se dice en la landing (es un diferencial, no un problema).

- [ ] 100% online, igual que Auto
- [ ] Asistido por ejecutivo → cómo lo describimos: ______________________

---

## 1. Propuesta de valor

- [ ] Bajada del hero (1-2 frases). Borrador actual: *"Compara las coberturas de las principales aseguradoras de Chile y elige la que te sirve. Te acompañamos en todo el proceso, sin letra chica."*
- [ ] Tercer punto de confianza del hero. Los dos primeros ya están fijos por convención del proyecto: "Todas las aseguradoras" y "100% online". En Auto el tercero es "En 5 minutos" — ¿cuál es el tiempo real de cotización en Salud? ______________________
- [ ] Copy del closer. Borrador actual: *"Encuentra el Seguro de Salud que de verdad te sirve."* (Auto usa *"Deja de pagar de más"*, que acá no aplica por 0.2)

## 2. Cómo funciona — los 3 pasos

Paso 2 ya está resuelto ("Mira todas tus opciones"). Faltan:

- [ ] **Paso 1 — qué datos pide el formulario.** En Auto: *"Cuéntanos de tu auto: patente o marca, modelo y año"*. En Salud: ¿isapre actual, edad, grupo familiar, renta? ______________________
- [ ] **Paso 3** — depende de la decisión 0.3

## 3. Coberturas / beneficios (3 o 4)

En Auto son: daños a terceros · robo total · choque y volcamiento · asistencia en ruta 24/7.
Cada una es título corto + una línea.

| # | Título | Descripción (1 línea) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 (opcional) | | |

Nota de assets: los íconos se reutilizan del design system (hoy calzan `small_icon_Seguro Salud`,
`small_icon_users`, `small_icon_headset`). Si quieres una 4a cobertura con ícono propio, hay que
crear ese `.svg` en el DS — no existe todavía.

## 4. Aseguradoras

Ya en la landing (logo disponible en el DS): **Consorcio · BCI · Zurich**.

- [ ] **Falta el logo de Alemana** en `brand/design-system/assets/` — es urgente, tiene ad group activo hoy en la cuenta
- [ ] **Falta el logo de Bupa** (estaba en el plan 1.4, sin ad group activo al último review)
- [ ] Confirmar si hay otra aseguradora que compita en Salud y no esté en esta lista: ______________________

Formato: `.svg` preferentemente, nombre `logo_Alemana.svg` / `logo_Bupa.svg`.

## 5. Imagen del hero

- [ ] `promo-salud-hero.png` — composición equivalente a `promo-auto-hero.png` (personaje + cartel). Sin promoción vigente, el cartel puede ser un mensaje de propuesta de valor en vez de un descuento.

Mientras no exista, la landing muestra el ícono de producto del DS como marcador de posición.

## 6. Promoción

El borrador **no tiene** sección de banner promocional (se eliminó completa, como manda el manual
cuando no hay oferta activa).

- [ ] No hay promoción vigente para Salud → dejar así
- [ ] Sí hay promoción → texto exacto con vigencia: ______________________ · y el PDF de condiciones alojado en Cloudinary (no en el File Manager de HubSpot)

## 7. Conversión — BLOQUEANTE

- [ ] **URL real del formulario de cotización de Salud.** En Auto es `https://seguro-auto.comparaonline.cl/quote`. Sin esta URL los CTA quedan inertes. ______________________
- [ ] Confirmar que se preserva `gclid` + `utm_*` en la redirección (es el default y no debería cambiar; solo confirmarlo)

## 8. Medición — BLOQUEANTE, y no está en el checklist original

Esto no venía en el traspaso y es lo que puede dejar la landing sin lectura:

- [ ] **`tracking_url_template` y `final_url_suffix` en la cuenta de HICL.** Al review del 22/06 estaban en `None` en **todas** las campañas de la cuenta, y Metabase mandaba casi todo HICL a `Google Generic Search / not known`. Sin esto no vamos a poder decir si la landing funcionó. (Revalidar: el dato es del 22/06.)
- [ ] **Baseline del test:** la landing nueva compite contra `https://www.comparaonline.cl/seguro-de-salud`, que es una página institucional, no una landing puente.
- [ ] **Tipo de test:** split-URL en AB Tasty (no modificación de elemento — la implementación actual en HubSpot inyecta el contenido por `fetch`, y eso rompe los tests por elemento).
- [ ] **Métrica de decisión:** venta por sale-date. No quote, no `match_sales` (infla ~2x).
- [ ] Confirmar que el evento de clic cuenta igual un clic en imagen que en botón real — en el caso Auto quedó como hipótesis abierta de subconteo.

## 9. Aprobaciones

- [ ] Quién aprueba copy y diseño antes de pasar a HubSpot: ______________________
- [ ] Quién publica en HubSpot y en qué dominio: ______________________

---

## Lo que ya está resuelto (no requiere trabajo tuyo)

- Estructura completa de la landing, patrón "landing puente" (un solo objetivo de conversión)
- Nav sin links que compitan con la conversión, logo apuntando al sitio corporativo
- CTA sticky en mobile, con la misma URL que el resto
- Reveals al hacer scroll, luz del hero, marquee de logos en mobile
- Preservación de `gclid` / `utm_*` implementada
- CTA con el mismo texto en sus 3 apariciones (patrón validado en Auto)
- Footer y favicon
- Link desde el Home (`index.html`) al botón de producto y a la tarjeta del carrusel
