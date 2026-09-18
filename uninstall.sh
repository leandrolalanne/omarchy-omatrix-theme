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

BGDIR="$CONFIG/omarchy/backgrounds/$SLUG"
if [[ -d $BGDIR ]]; then
  rm -rf "$BGDIR"; echo "removed $BGDIR"; removed=1
fi

(( removed )) || echo "nothing to remove"
echo
echo "NOTE: if omatrix is the current theme, pick another one:  omarchy theme set <name>"
