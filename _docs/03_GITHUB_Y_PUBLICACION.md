# 03 — GitHub y publicación

## El repositorio real

El caso de éxito vive en `cperez-brand/landings-compara` en GitHub (rama `main`). El contenido de `source/` en este paquete es una copia exacta de ese repositorio al momento del traspaso.

Si quien recibe este paquete va a seguir trabajando **sobre ese mismo repositorio**, necesita que le den acceso de colaborador (o se crea un repositorio nuevo, propio del equipo, usando `source/` como punto de partida — ambas opciones son válidas, es una decisión de a quién le pertenece el proyecto de aquí en adelante).

## Cómo se sube el trabajo

El patrón real usado en el caso Auto es simple: **un commit por tanda de cambios**, con mensaje corto que indica qué landing se tocó y qué se cambió. Ejemplos reales del historial:

```
auto: hover del CTA del hero a #4168FF y quitar la flecha
home: elimina seccion aseguradoras; chat rediseñado...
auto (mobile): separar CTA de la imagen — imagen limpia arriba, boton real debajo...
```

Convención observada:
- Prefijo con el nombre de la landing afectada (`auto:`, `home:`, o `ambas:` si el cambio toca las dos)
- Si el cambio es solo para mobile, se indica entre paréntesis: `auto (mobile): ...`
- Mensajes en minúsculas, directos, sin punto final
- Cuando el cambio se hizo con ayuda de Claude Code/Opus, el commit queda co-autoreado (`Co-Authored-By: Claude Opus 4.8`) — mantén esta práctica de trazabilidad si aplica

## Previsualización (GitHub Pages)

El repositorio tiene GitHub Pages habilitado. Con la configuración por defecto de GitHub (repo público, Pages activado desde `Settings → Pages`, rama `main`, carpeta raíz), la URL de previsualización sigue el patrón:

```
https://cperez-brand.github.io/landings-compara/index.html
https://cperez-brand.github.io/landings-compara/auto.html
```

**A confirmar antes de asumir esta URL como definitiva:** que Pages siga activo en `Settings → Pages` del repositorio, y si hay un dominio personalizado (CNAME) configurado — el repo no tenía un archivo `CNAME` al momento de este traspaso, así que por defecto debería estar sirviendo desde el subdominio `github.io`.

Esta URL de Pages es útil para:
- Compartir un link de revisión con quien tenga que aprobar copy/diseño (paso 5 del checklist de requisitos)
- Verificar en un dispositivo real antes de pasar a HubSpot

## Qué sigue después de aprobado

Una vez que la landing nueva está aprobada visualmente en GitHub Pages, el siguiente paso es llevarla a HubSpot como página real de producción — ver `04_IMPLEMENTACION_HUBSPOT.md`.
