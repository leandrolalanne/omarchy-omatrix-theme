# omarchy-matrix-theme

Tema estilo *The Matrix* para [Omarchy](https://omarchy.org/).

Slug al instalar: **`matrix`** (`omarchy theme install` quita `omarchy-` y `-theme`).

```bash
omarchy theme install <git-url>
omarchy theme set matrix
```

## Estructura

| Ruta             | Qué va acá |
|------------------|------------|
| `colors.toml`    | Paleta única. Omarchy genera desde acá los configs de terminal, btop, neovim, hyprland, shell, chromium, vscode. **Placeholder por ahora.** |
| `screensaver/`   | Screensaver del tema. **Punto de partida — en desarrollo.** |
| `branding/`      | Assets de branding (`screensaver.txt` y demás ASCII art). |
| `backgrounds/`   | Wallpapers del tema. |
| `scripts/`       | `install.sh` / `uninstall.sh` y utilidades. |
| `docs/`          | Notas de diseño y documentación. |

Archivos de tema todavía no creados: `icons.theme`, `neovim.lua`, `vscode.json`,
`preview.png`, `preview-unlock.png`, `unlock.png`, `shell.*.toml`.

## Nota sobre themes clonados

Omarchy descarta de un tema clonado por git todo lo que ejecuta código
(`*.lua`, `alacritty.toml`, `foot.ini`, `ghostty.conf`, `kitty.conf`,
`vscode.json`) y lo regenera desde `colors.toml`. Se conservan `btop.theme`,
`chromium.theme`, `helix.toml`, `icons.theme`, `keyboard.rgb` y `shell.toml`.

## Estado

- [ ] Screensaver
- [ ] Paleta definitiva
- [ ] Backgrounds
- [ ] Previews / unlock
- [ ] Shell (bar, launcher, menu, notifications)
- [ ] install.sh / uninstall.sh
