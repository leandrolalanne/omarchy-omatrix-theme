#!/bin/bash
# Install omatrix: the theme, its font hook, and the background machinery.
#
#   ./install.sh          link the theme and install the plugin
#   ./uninstall.sh        undo it
#
# The theme is linked rather than copied so edits are live. Omarchy stages a
# copy of its own on every `theme set`, so the link is never what Hyprland
# reads -- which is also why any edit needs a re-stage to show up.

set -uo pipefail

SLUG="omatrix"
PLUGIN_ID="lean.omatrix"
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
THEMES="$CONFIG/omarchy/themes"
PLUGINS="$CONFIG/omarchy/plugins"
HOOKS="$CONFIG/omarchy/hooks/theme-set.d"
# Read live by Omarchy and listed BEFORE the theme's own, so a background
# dropped here needs no re-stage.
BGDIR="$CONFIG/omarchy/backgrounds/$SLUG"

command -v omarchy >/dev/null || { echo "install: this needs Omarchy." >&2; exit 1; }

# --- the theme ---
mkdir -p "$THEMES"
ln -sfn "$SRC" "$THEMES/$SLUG"
echo "linked   $THEMES/$SLUG"

# --- the font hook ---
mkdir -p "$HOOKS"
install -m 755 "$SRC/hooks/theme-set.d-omatrix" "$HOOKS/$SLUG"
echo "linked   $HOOKS/$SLUG"

# --- the background machinery ---
mkdir -p "$PLUGINS"
ln -sfn "$SRC/plugin" "$PLUGINS/$PLUGIN_ID"
echo "linked   $PLUGINS/$PLUGIN_ID"

# --- the backgrounds, from the provider ---
# The rain is not in this repo. omatrix is the consumer: it mounts whatever
# matrix-rain declares in its provider.json, and the version of each live
# wallpaper is carried in its filename.
PROVIDER=""
for d in "$HOME/.local/share/matrix-rain" /usr/share/matrix-rain; do
  [[ -d $d/assets/backgrounds ]] && { PROVIDER="$d"; break; }
done

if [[ -n $PROVIDER ]]; then
  mkdir -p "$BGDIR"
  n=0
  for f in "$PROVIDER"/assets/backgrounds/*.live.*; do
    [[ -e $f ]] || continue
    cp "$f" "$BGDIR/"; n=$((n + 1))
  done
  echo "copied   $n live backgrounds into $BGDIR"
else
  echo
  echo "NOTE: the matrix-rain provider is not installed, so there are no live"
  echo "      backgrounds yet. Install it and re-run this script:"
  echo "        git clone https://github.com/leandrolalanne/matrix-rain"
  echo "        cd matrix-rain && ./install.sh"
fi

# The default still-image wallpaper travels with the theme itself, so it is
# already in place through the link above.

# The link above may not have been picked up by plugin discovery yet, so give
# it a second try rather than reporting a failure that fixes itself.
if omarchy plugin enable "$PLUGIN_ID" >/dev/null 2>&1 \
   || { sleep 1; omarchy plugin enable "$PLUGIN_ID" >/dev/null 2>&1; }; then
  echo "enabled  $PLUGIN_ID"
else
  echo "NOTE: could not enable $PLUGIN_ID; run: omarchy plugin enable $PLUGIN_ID"
fi

echo
echo "Done. Apply it with:  omarchy theme set $SLUG"
echo "Then cycle wallpapers to reach the live ones (Super+Ctrl+Space, or"
echo "'omarchy theme bg next'). Selecting one turns the rain on."
