#!/bin/bash
# Remove what install.sh put in place. Leaves this source tree alone.
set -uo pipefail

SLUG="omatrix"
PLUGIN_ID="lean.omatrix"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"

removed=0
# -L before any rm: these are links into the source tree, and following one
# would delete the repo instead of the link.
for link in "$CONFIG/omarchy/themes/$SLUG" "$CONFIG/omarchy/plugins/$PLUGIN_ID"; do
  [[ -L $link ]] || continue
  omarchy plugin disable "$PLUGIN_ID" >/dev/null 2>&1
  rm -f "$link"; echo "removed $link"; removed=1
done

for f in "$CONFIG/omarchy/hooks/theme-set.d/$SLUG" "$CONFIG/omarchy/hooks/post-boot.d/$SLUG"; do
  [[ -e $f ]] || continue
  rm -f "$f"; echo "removed $f"; removed=1
done

# The hook keeps a copy of whatever branding was there before omatrix. If it
# is still around, omatrix never handed it back -- do it here.
SAVED="$CONFIG/omarchy/branding/screensaver.txt.pre-omatrix"
if [[ -f $SAVED ]]; then
  cp "$SAVED" "$CONFIG/omarchy/branding/screensaver.txt" && rm -f "$SAVED"
  echo "restored $CONFIG/omarchy/branding/screensaver.txt"; removed=1
fi

GHOSTTY="$CONFIG/ghostty/config"
if [[ -w $GHOSTTY ]] && grep -qF 'current/theme/omatrix.conf' "$GHOSTTY"; then
  sed -i '/# omatrix: terminal translucency/d; \|current/theme/omatrix\.conf|d' "$GHOSTTY"
  echo "unpatched $GHOSTTY"; removed=1
fi

BGDIR="$CONFIG/omarchy/backgrounds/$SLUG"
if [[ -d $BGDIR ]]; then
  rm -rf "$BGDIR"; echo "removed $BGDIR"; removed=1
fi

FLAGS="$CONFIG/chromium-flags.conf"
if [[ -w $FLAGS ]] && grep -q "whatsapp-omatrix" "$FLAGS"; then
  sed -i 's|,[^,]*whatsapp-omatrix||g' "$FLAGS"
  echo "unpatched $FLAGS"; removed=1
fi

WELCOME="$HOME/.local/bin/omarchy-terminal-welcome"
if [[ -w $WELCOME ]] && grep -q '  omatrix)' "$WELCOME"; then
  sed -i '/# omatrix ships its own banner/d; /^  omatrix) exec /d' "$WELCOME"
  echo "unpatched $WELCOME"; removed=1
fi

STATE="$HOME/.local/state/omatrix"
if [[ -d $STATE ]]; then
  rm -rf "$STATE"; echo "removed $STATE"; removed=1
fi

# The screensaver shim is the one thing that lives outside $HOME, so it is not
# removed here: this script does not ask for root, and should not.
if [[ -e /usr/local/bin/omarchy-screensaver ]]; then
  echo
  echo "NOTE: the forced matrix screensaver effect is still installed. Remove it with:"
  echo "      sudo $(dirname "${BASH_SOURCE[0]}")/scripts/install-screensaver-effect.sh --remove"
fi

(( removed )) || echo "nothing to remove"
echo
echo "NOTE: if omatrix is the current theme, pick another one:  omarchy theme set <name>"
