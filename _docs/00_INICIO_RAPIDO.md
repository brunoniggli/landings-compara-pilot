# 00 — Inicio rápido

## En una frase

Compara tiene una landing de marca ("Home") y una landing de producto ya aprobada e implementada en HubSpot ("Seguro de Auto", campaña interna **CICL**). Este paquete permite clonar el patrón de esa landing de producto para crear landings de otros seguros (vida, salud, viaje, SOAP...), reutilizando el mismo design system, el mismo CSS/JS compartido y los mismos aprendizajes de UX que ya se validaron con el negocio.

## Los dos archivos de referencia y su rol

### `source/index.html` — "Home"
Es la landing de marca: vitrina con **todos** los productos de seguros, hero con botones para elegir qué cotizar, demo de un chat de asesor IA ("Compa"), carrusel de productos y una sección "cómo funciona" genérica. Su función es ser el **KV** (Key Visual) de la marca — el lugar donde alguien llega sin saber qué necesita todavía y elige.

**Home no es la plantilla a clonar.** Es la referencia visual de marca (tipografía, nav, tono) y el lugar donde se agrega la tarjeta/botón que apunta a cada landing de producto nueva.

### `source/auto.html` — "Seguro de Auto" (CICL)
Es la landing de **un solo producto y un solo objetivo**: que la persona cotice su Seguro de Auto. No tiene navegación a otras secciones, tiene un solo tipo de CTA repetido varias veces ("Cotiza tu Seguro de Auto"), muestra las aseguradoras específicas de ese producto, sus coberturas, y termina con un CTA sticky en mobile.

**Esta es la plantilla a clonar.** Fue iterada con datos reales (A/B tests, rondas de feedback del negocio) hasta llegar al estado que se implementó en HubSpot. Todo ese historial de decisiones está en `05_APRENDIZAJES_CASO_CICL.md` — vale la pena leerlo antes de tocar nada, para no repetir pruebas que el equipo ya hizo.

## Por qué está separado en carpetas

```
source/
├── index.html, auto.html        ← el HTML de cada landing (uno por producto)
├── assets/                       ← imágenes específicas de UNA landing (ej. el hero promocional de Auto)
├── brand/design-system/          ← lo que es de MARCA: colores, tipografía, logos de aseguradoras,
│                                    íconos de producto, fuentes. Se reutiliza en todas las landings.
└── shared/                       ← compara.css y compara.js: el comportamiento y estilo BASE
                                     que comparten todas las landings (nav, reveals al hacer scroll,
                                     CTA sticky, carrusel, etc.)
```

La razón de esta separación: cuando se cree la landing de "Seguro de Vida", **no** hay que tocar `brand/` ni `shared/` — solo se agregan los assets nuevos de esa landing (en su propia carpeta `assets/`, o una subcarpeta si se prefiere) y se escribe el HTML nuevo reutilizando lo que ya existe.

## Es 100% estático — sin build, sin frameworks

`index.html` y `auto.html` son HTML puro con CSS y JS vainilla. Las únicas dependencias externas son:
- Google-free: las fuentes (Poppins, Open Sans, DM Serif Display) están auto-alojadas como archivos `.ttf` en `brand/design-system/fonts/`, no vienen de Google Fonts.
- Un solo script externo por CDN: [Lucide](https://lucide.dev/) (`unpkg.com/lucide@latest`) para los íconos de interfaz (flechas, check, menú, etc.)

Esto significa que cualquier landing de este proyecto se puede abrir directo desde el explorador de archivos (doble clic al `.html`) sin instalar nada, y también se puede pegar tal cual en un módulo de HTML de HubSpot. Ver `04_IMPLEMENTACION_HUBSPOT.md` para ese paso.
