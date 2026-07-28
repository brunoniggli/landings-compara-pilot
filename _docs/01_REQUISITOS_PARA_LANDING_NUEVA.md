# 01 — Requisitos para crear una landing nueva

Antes de pedirle a Claude Code que arme la landing de un producto nuevo (ej. Seguro de Vida, Salud, Viaje, SOAP), reúne esto. Es exactamente lo que existe hoy para Seguro de Auto — si algo de esta lista no está listo, la landing va a salir con placeholders y TODOs, igual que salió `auto.html` en sus primeras versiones (ver `05_APRENDIZAJES_CASO_CICL.md`).

## 1. Producto y propuesta de valor

- [ ] Nombre exacto del producto, con mayúsculas correctas (ej. "Seguro de Vida", no "seguro vida")
- [ ] Una bajada corta de propuesta de valor para el `<title>` y meta description (1 frase, ~20 palabras)
- [ ] 3 puntos de confianza cortos para el hero (en Auto son: "Todas las aseguradoras" / "100% online" / "En 5 minutos")
- [ ] 3 pasos de "cómo funciona", cada uno con: título corto + 1-2 líneas de descripción
- [ ] 3 a 4 coberturas o beneficios principales, cada uno con: título, descripción corta, e idea de qué ícono usar

## 2. Assets visuales

- [ ] Ícono pequeño del producto (formato como `small_icon_Seguro Auto.svg`) — se usa en el nav de Home y en bullets
- [ ] Ícono grande del producto (formato como `icon_Seguro Auto.svg`) — se usa en tarjetas y carrusel
  - *Si el producto ya tiene ícono en `brand/design-system/assets/` (revisar la lista: Asistencia Viaje, SOAP, Seguro Salud, Seguro Vida, Crédito Hipotecario), no hace falta crear uno nuevo.*
- [ ] Imagen hero promocional (composición tipo `promo-auto-hero.png`: personaje + cartel de oferta), en desktop y, si el diseño lo amerita, una versión mobile aparte
- [ ] Banner promocional desktop + mobile, **solo si hay una oferta/descuento vigente** para ese producto (si no hay promo activa, se omite todo el bloque — ver `02_MANUAL_CREAR_LANDING.md`)
- [ ] Lista de logos de aseguradoras que compiten en ese producto (pueden ser las mismas 10 de Auto, o un subconjunto distinto — confirmarlo, no asumir)

## 3. Copy legal / comercial

- [ ] Si hay promoción vigente: PDF de condiciones generales, ya alojado en un host estable (Cloudinary u otro — **no** HubSpot File Manager, ver nota en `04_IMPLEMENTACION_HUBSPOT.md`)
- [ ] Texto exacto de la oferta, con vigencia (ej. "Hasta 20% de descuento en tus primeras 12 cuotas")

## 4. Integración de conversión

- [ ] **URL real del formulario de cotización** para ese producto específico (reemplaza el placeholder `FORM` del script — sin esto la landing queda con los botones inertes, igual que Auto en sus primeras versiones)
- [ ] Confirmar que se debe preservar `gclid` y `utm_*` en la redirección (es el comportamiento por defecto ya usado en Auto; solo cambiar si el equipo de performance/paid media pide algo distinto)

## 5. Aprobaciones

- [ ] Quién en el equipo aprueba el copy y el diseño antes de pasar a HubSpot (si no está definido, dejarlo como pendiente explícito — no asumir que "queda aprobado" solo porque el HTML está listo)

---

**Regla para Claude Code:** si alguno de estos puntos no está resuelto, no lo inventes. Deja el mismo tipo de placeholder visible y comentado que usa `auto.html` (ver los comentarios `<!-- TODO: ... -->` y la variable `FORM` en el script final) y avísale explícitamente a la persona qué falta.
