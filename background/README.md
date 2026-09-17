# Background animado

La lluvia de [Rezmason/matrix](https://github.com/Rezmason/matrix) renderizada
**en vivo** como fondo de escritorio, en la capa layer-shell real.

```bash
background/bin/matrix-background                    # preset por defecto: classic
background/bin/matrix-background --version operator
background/bin/matrix-background --param numColumns=60
background/bin/matrix-background --list
background/bin/matrix-background --print-url        # sin abrir nada
```

Se apaga con Ctrl+C o `SIGTERM`. Config opcional del usuario:
`~/.config/omarchy/matrix-background.conf` (mismo formato `clave=valor`).

## Costo en recursos — medido, no estimado

| | |
|---|---|
| CPU en estado estable | **~35% de un core** (2 monitores, 60fps) |
| RAM | **~880 MB** |
| Procesos | 1 python + 1 WebKitNetworkProcess + **1 WebKitWebProcess por monitor** |

Los ~880 MB son el grueso del costo: cada monitor levanta un proceso WebKit
completo. Con un solo monitor es aproximadamente la mitad.

**`--fps 30` no ayuda.** Medido: 34.7% a 60fps contra 36.1% a 30fps, o sea
dentro del ruido. El parametro `fps` de Rezmason regula el timing interno de la
animacion, no el loop de render, asi que no sirve para ahorrar bateria. La
unica palanca real es no correrlo, o correrlo en menos monitores.

## Por que esta implementado asi

Tres caminos se probaron y dos se cayeron:

**Chromium no puede ser wallpaper.** No habla layer-shell, y Hyprland 0.56.2 no
tiene regla para mandar una ventana atras de todo. Una ventana flotante queda
POR ENCIMA de las tiladas, que es exactamente lo contrario de un fondo.

**QtWebEngine dentro de Quickshell se cae.** Meter el render en el plugin de
fondo de Omarchy seria lo mas integrado, pero QtWebEngine aborta con
`FATAL: Argument list is empty, the program name is not passed to
QCoreApplication` y deja core dump. Como ese proceso tambien dibuja la barra,
las notificaciones y el lock, un fallo ahi se lleva puesta la sesion entera.
(QtMultimedia si carga bien en Quickshell, por si alguna vez se quiere la via
de un loop en video en lugar de render vivo.)

**GTK3 + gtk-layer-shell + WebKit2GTK si funciona.** Crea una superficie
layer-shell propia en la capa `BACKGROUND` y embebe el render de upstream sin
tocarlo. Verificado en vivo: canvas 2305x1296, 60 fps exactos, sin el aviso de
"no GPU" que Rezmason muestra cuando cae a software. Todas las dependencias ya
venian instaladas en el sistema.

## Detalles que importan

**Region de input vacia.** La superficie se dibuja encima del wallpaper de
Omarchy (misma capa, creada despues) pero no recibe clicks: los deja pasar al
fondo de abajo, asi el doble click que abre el selector de temas sigue andando.

**Hotplug de monitores.** Se escucha `monitor-added` / `monitor-removed` del
display, asi enchufar o desenchufar una pantalla crea o destruye su superficie
sola. Sin eso, un monitor enchufado despues quedaria sin fondo.

**Sin overlay.** Al reves del screensaver, el fondo NO inyecta `exit.js`:
un wallpaper no debe cerrarse cuando tocas una tecla.

**`exclusive_zone = -1`.** Ni reserva espacio ni respeta el de otros, que es lo
que corresponde a algo que ocupa la pantalla completa por debajo de todo.

## Arranque automatico

Todavia no esta cableado. No se agrego solo porque implica tocar la config de
la sesion. Las dos opciones:

```bash
# Hyprland, en ~/.config/hypr/autostart.lua o equivalente
o.exec_once("<ruta>/background/bin/matrix-background")
```

o un servicio de usuario systemd, que ademas lo reinicia si se cae.
