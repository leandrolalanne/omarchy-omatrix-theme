# Screensaver

Lluvia Matrix sobre [Rezmason/matrix](https://github.com/Rezmason/matrix) (WebGL, MIT),
la implementacion mas fiel a la pelicula que existe.

```bash
bin/matrix-screensaver                      # preset por defecto: operator
bin/matrix-screensaver --version classic
bin/matrix-screensaver --param numColumns=60 --param fallSpeed=0.3
bin/matrix-screensaver --list               # presets disponibles
bin/matrix-screensaver --print-url          # URL resuelta, sin abrir nada
```

Sale con cualquier tecla, click, rueda o movimiento de mouse, igual que el
screensaver stock de Omarchy.

## Como funciona

```
bin/matrix-screensaver                    launcher
  └─ bin/matrix-screensaver-server        HTTP efimero en 127.0.0.1:<puerto libre>
       ├─ sirve vendor/matrix/            copia sin tocar de upstream
       ├─ inyecta overlay/exit.js         en el HTML, al vuelo
       └─ /__exit                         la pagina avisa que hubo input
  └─ chromium --kiosk                     una ventana por monitor
```

## Decisiones y por que

**Hace falta un servidor HTTP.** `index.html` de upstream carga
`<script type="module">`, y Chromium bloquea modulos ES sobre `file://` por CORS.
El propio README de upstream sugiere `python3 -m http.server`. Usamos loopback
en un puerto libre al azar.

**`--kiosk`, no `--app`.** Verificado a mano: en modo `--app` Chromium ignora
`--class` y deriva el app_id de la URL (`chrome-127.0.0.1__-Default`), con lo
cual no matchean las windowrules de Omarchy. En `--kiosk` si respeta `--class`,
y la ventana toma `org.omarchy.screensaver` — la misma clase que ya matchea
`/usr/share/omarchy/default/hypr/apps/system.lua:35-37` para fullscreen.

**Un perfil de Chromium por ventana.** Con un `--user-data-dir` compartido, la
segunda invocacion le habla al proceso ya abierto y la ventana hereda la clase
de la primera en vez de crear la suya. Van a `$XDG_RUNTIME_DIR` y se borran al salir.

**La salida por mouse se arma por quietud, no por tiempo fijo.** La windowrule
de Omarchy usa `animation = "slide"`: la ventana entra deslizandose por debajo
de un cursor quieto y emite un chorro de `mousemove` con coordenadas que cambian
solas. Un umbral de distancia con delay fijo se disparaba siempre. `exit.js`
arma el mouse recien tras `SETTLE_MS` sin eventos; teclado, click y rueda no
tienen fuente espuria y se arman con un piso corto.

**`vendor/matrix/` no se edita.** Es la copia de upstream tal cual, con su
`LICENSE` y el commit anotado en `UPSTREAM`. Todo lo nuestro vive en `overlay/`
y lo inyecta el servidor. Asi actualizar upstream es reemplazar el directorio.

**Vendorizado y no submodulo.** `omarchy theme install` hace `git clone` pelado,
sin `--recurse-submodules`: un submodulo llegaria vacio al usuario.

## Presets

| Preset | Que es |
|--------|--------|
| `operator` | El codigo de los titulos de la primera pelicula y las pantallas de los operadores: plano, apretado, sin gradiente, con ripples cuadrados. **Default.** |
| `classic` | El codigo de los titulos de las secuelas. El default de upstream. |
| `resurrections` | El codigo actualizado de *Resurrections*, con fuente propia y glint. |
| `megacity` | Como `classic` pero con la Megaciudad como glifo, de *Revolutions*. |

Un preset es un archivo `clave=valor` que termina como query string. El
`version=` trae toda la base desde `vendor/matrix/js/config.js`; lo demas
sobreescribe encima. La lista completa de parametros esta en el README de upstream.

Precedencia: preset < `~/.config/omarchy/matrix-screensaver.conf` < `--param`.

## Estado verificado

- [x] Renderiza (`operator`, 1920x1080, fullscreen)
- [x] La ventana toma `org.omarchy.screensaver` y hereda las windowrules
- [x] Estable: 12s sin cerrarse solo
- [x] Sale con teclado (`exit: keydown`)
- [x] Oculta y restaura el cursor
- [x] No deja procesos ni perfiles colgados
- [ ] Salida por movimiento de mouse: el handler esta cableado y se lo vio
      disparar, pero no se pudo confirmar contra un mouse movido a mano —
      `hyprctl dispatch movecursor` teletransporta el cursor sin entregarle
      evento de movimiento al cliente.
- [ ] Enganche al idle de Omarchy (etapa siguiente)

## Pendiente: enganche al idle

El servicio idle corre `omarchy-launch-screensaver` via `bash -lc`
(`/usr/share/omarchy/shell/plugins/services/idle/Service.qml:69`). Shadowearlo
por PATH **no funciona**: aun en login shell `/usr/bin` gana sobre
`~/.local/bin`. La via correcta es clonar el plugin con
`omarchy plugin clone omarchy.idle` y cambiar ahi el comando.
