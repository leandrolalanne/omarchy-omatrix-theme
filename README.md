# omarchy-matrix-theme

A *Matrix*-styled theme for [Omarchy](https://omarchy.org/).

Slug on install: **`matrix`** (`omarchy theme install` strips the `omarchy-`
prefix and the `-theme` suffix).

## Status: a structure, waiting

This repo started out as a complete implementation on top of
[Rezmason/matrix](https://github.com/Rezmason/matrix) running in WebGL: a
screensaver in a Chromium kiosk and an animated background in WebKit on a
layer-shell surface. It worked, and it cost **~880 MB of RAM and ~35% of one
core** with two monitors, because every screen brought up a full WebKit process.

That implementation has been **retired**. The effect became a project of its own:

> **[omarchy-matrix-rain](../omarchy-matrix-rain)** — the rain ported to a native
> Qt Quick shader. A single `ShaderEffect` instead of upstream's four ping-pong
> buffers, with a 5-level bloom and a terminal layout model (point size drives
> the cell, the window decides how many columns fit).

Everything that comes back here will come from there: screensaver, background,
generated art. This repo stays as the structure to be filled in **later**, once
that project is done.

The history is intact: the WebGL implementation can be recovered from git at any
time.

## Structure

| | |
|---|---|
| `colors.toml` | the palette. **Still a placeholder** |
| `backgrounds/` | the theme's wallpapers |
| `branding/` | ASCII art and branding assets |
| `scripts/` | installer and utilities |
| `docs/` | design notes |

## Still to do

- **The palette.** Open question about which green to derive it from: Rezmason's
  `operator` (hue 144, from reference work on home video transfers), the popular
  `#00FF41` palette (~135, fan-made and with inconsistent hues), or sampling a
  frame of the film. There is no officially declared studio color.
- Whatever `omarchy-matrix-rain` contributes once it is packaged as a plugin.
- Backgrounds, previews and the unlock image.
