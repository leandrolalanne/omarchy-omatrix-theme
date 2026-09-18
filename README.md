# omarchy-matrix-theme

Tema estilo *The Matrix* para [Omarchy](https://omarchy.org/).

Slug al instalar: **`matrix`** (`omarchy theme install` quita `omarchy-` y `-theme`).

## Estado: estructura, esperando

Este repo arranco siendo una implementacion completa sobre
[Rezmason/matrix](https://github.com/Rezmason/matrix) corriendo en WebGL:
screensaver en Chromium kiosk y fondo animado en WebKit sobre layer-shell.
Funcionaba, y costaba **~880 MB de RAM y ~35% de un core** con dos monitores,
porque cada pantalla levantaba un proceso WebKit completo.

Esa implementacion **se retiro**. El efecto se convirtio en un proyecto propio:

> **[omarchy-matrix-rain](../omarchy-matrix-rain)** — la lluvia portada a un
> shader nativo de Qt Quick. Un solo `ShaderEffect` en vez de los cuatro
> ping-pong buffers del original, con bloom de 5 niveles y modelo de layout de
> terminal (el cuerpo en puntos manda, la ventana decide cuantas columnas entran).

De ahi va a salir todo lo que vuelva aca: screensaver, fondo, generacion de arte.
Este repo queda como la estructura que se completa **despues**, cuando ese
proyecto este terminado.

El historial esta intacto: la implementacion WebGL se puede recuperar de git
en cualquier momento.

## Estructura

| | |
|---|---|
| `colors.toml` | la paleta. **Todavia placeholder** |
| `backgrounds/` | wallpapers del tema |
| `branding/` | ASCII art y assets de branding |
| `scripts/` | instalador y utilidades |
| `docs/` | notas de diseño |

## Pendiente

- **La paleta.** Decision abierta sobre de que verde derivarla: el `operator` de
  Rezmason (hue 144, de investigacion sobre transfers de home video), la paleta
  popular `#00FF41` (~135, fan-made y con los hues inconsistentes), o muestrear
  un frame de la pelicula. No existe un color oficial declarado por el estudio.
- Lo que aporte `omarchy-matrix-rain` una vez empaquetado como plugin.
- Backgrounds, previews y unlock.
