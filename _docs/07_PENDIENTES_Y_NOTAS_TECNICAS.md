# 07 — Pendientes abiertos y notas técnicas

Todo lo de este documento viene del relato directo de la sesión de Claude Code donde se implementó la landing de Auto en HubSpot (no de los commits de GitHub, que ya están cubiertos en `05_APRENDIZAJES_CASO_CICL.md`). Se agrupa acá porque son datos operativos y de estado del proyecto, no aprendizajes de diseño.

## Pendientes abiertos (verificar antes de asumir que están resueltos)

- [ ] **Dominio y publicación de la landing de Auto en HubSpot.** Al cierre de esa sesión, la página seguía en estado borrador, apuntando por error al dominio de Vida (`segurovida.comparaonline.cl`) en vez del dominio deseado (`seguro.comparaonline.cl`). Carlos tomó la tarea de corregir el dominio y publicar por su cuenta — no hay confirmación de que ya se haya hecho. **Verificar directamente en HubSpot antes de dar esto por publicado.**
- [ ] **Decisión sobre la "Opción B"** (template custom-coded server-rendered vía HubSpot CLI, sin `fetch`/async) — quedó solo planteada como recomendación si el enfoque actual (loader + fetch) resulta insuficiente para tests de AB Tasty por modificación de elementos. No se ejecutó en ninguna sesión.
- [ ] **Rol/plan exacto de HubSpot de Carlos** — se usó una cuenta con permiso de lectura/escritura sobre `LANDING_PAGE`, pero no quedó documentado si es Marketing Hub Professional, Enterprise, etc. Relevante si el equipo nuevo necesita replicar accesos.
- [ ] **Cuenta de Cloudinary** donde vive el PDF de condiciones de la promoción (`res.cloudinary.com/compara/...`) — no se confirmó si es de uso general del equipo de marketing o específica de esta campaña.
- [ ] **Significado de "CICL"** — nunca se explicó ni se preguntó en ninguna sesión disponible. Aparece solo como parte del nombre de carpeta del PDF en Cloudinary (`CICL_20dcto_Junio_2026`). Si alguien del equipo sabe qué significa, vale la pena agregarlo al glosario.

## Notas sobre el diseño fuente (Figma)

Los ajustes de diseño de la sesión de HubSpot vinieron de una **imagen de maqueta pegada directamente en el chat**, no de un archivo Figma enlazado. Sí existe, a nivel de proyecto (no específico de esta landing), una carpeta `brand/figma-exports/` con cerca de 130 láminas del brandbook general de la marca — es material de referencia de marca, no un diseño de landing dedicado. Si el equipo nuevo necesita el diseño fuente exacto de Auto en Figma, probablemente no exista como tal — el código (`source/auto.html`) es la fuente de verdad más confiable.

## Gotchas técnicos para quien continúe este proyecto

### 1. Rutas relativas al aplanar para GitHub Pages
Los archivos HTML fuente originales usan rutas del tipo `../brand/design-system/...`. Al aplanar todo a una carpeta de publicación (con `index.html` en la raíz, como está estructurado `source/` en este mismo paquete), esas rutas deben reescribirse a `brand/...` **sin** el `../` — si no, rompe en producción. (El `source/` de este paquete ya está aplanado correctamente; este aviso aplica si alguien vuelve a mover archivos de carpeta.)

### 2. Previsualización local en macOS
En el Mac usado para este proyecto, macOS bloquea (permisos TCC) levantar un servidor local apuntando a una ruta dentro de `Desktop`. El workaround fue copiar la carpeta de publicación a una ruta fuera de `Desktop` (ej. `/private/tmp/...`) antes de levantar un servidor Python + Playwright para previsualizar. Si alguien más se topa con un servidor local que no sirve archivos o da error de permisos sin motivo aparente en Mac, este es probablemente el motivo.

### 3. Protocolo de seguridad para el token de GitHub
En algún momento de este proyecto, el único conector de GitHub disponible era de solo lectura, así que la publicación real a GitHub Pages se hizo con `git` + un **token de acceso personal de un solo uso**. El protocolo seguido (y que conviene mantener con cualquier persona nueva que haga deploys):

1. Generar un token de un solo uso, con el mínimo permiso necesario
2. Clonar el repo con ese token
3. Hacer el push
4. Borrar el clon local
5. Verificar que no queden rastros del token en disco
6. Revocar el token en GitHub inmediatamente después de usarlo

Este protocolo no es opcional ni una formalidad — es la forma correcta de trabajar con credenciales temporales y vale la pena que el equipo nuevo lo siga igual.

## Para más detalle

El detalle técnico línea por línea de todo lo anterior (selectores CSS exactos, comportamiento completo del loader, contentId, etc.) vive en el memory file `project-hubspot-landing.md` de la sesión de Claude Code original. Este documento es un resumen — si algo no está claro, ese archivo (si se tiene acceso a esa sesión) tiene el nivel más granular.
