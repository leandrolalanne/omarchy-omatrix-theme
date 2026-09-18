#!/bin/bash
# Install (or remove) the two shims the screensaver needs.
#
#   ttfx      pins the effect to matrix instead of a random one
#   ghostty   sets the point size to 9 instead of the hardcoded 18
#
# Both are inert unless omatrix is the current theme, and ghostty's also checks
# that the invocation is the screensaver's. Neither can be done any other way:
# the values are command line arguments inside Omarchy's own launcher, which
# sits ahead of /usr/local/bin in the PATH and cannot itself be shimmed.
#
#   sudo scripts/install-screensaver-effect.sh
#   sudo scripts/install-screensaver-effect.sh --remove
#
# Separate from install.sh, and never run by it, because this is the only part
# of omatrix that writes outside $HOME. It needs root, it is system-wide, and a
# theme should not quietly take that. See scripts/system/omarchy-screensaver for
# why /usr/local/bin is the right place and ~/.local/bin cannot work.

set -uo pipefail
SRC="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# ttfx and not omarchy-screensaver: Omarchy's own bin directory precedes
# /usr/local/bin in the login PATH, so a shim for its script is never reached.
# ttfx exists only in /usr/bin, which /usr/local/bin does precede.
SHIMS=(ttfx ghostty)
OLD_BIN=/usr/local/bin/omarchy-screensaver
OLD_LIB=/usr/local/libexec/omatrix

(( EUID == 0 )) || { echo "This one needs root: sudo $0 $*" >&2; exit 1; }

# An earlier version shimmed omarchy-screensaver, which never ran. Clear it.
clear_old() {
  [[ -e $OLD_BIN ]] && { rm -f "$OLD_BIN"; echo "removed $OLD_BIN (never reached)"; }
  [[ -d $OLD_LIB ]] && { rm -rf "$OLD_LIB"; echo "removed $OLD_LIB"; }
  return 0
}

if [[ ${1:-} == --remove ]]; then
  removed=0
  for s in "${SHIMS[@]}"; do
    [[ -e /usr/local/bin/$s ]] || continue
    rm -f "/usr/local/bin/$s"; echo "removed /usr/local/bin/$s"; removed=1
  done
  clear_old
  (( removed )) || echo "nothing to remove"
  exit 0
fi

for s in "${SHIMS[@]}"; do
  [[ -x /usr/bin/$s ]] || { echo "/usr/bin/$s is missing; nothing to shim." >&2; exit 1; }
done

clear_old
for s in "${SHIMS[@]}"; do
  install -Dm755 "$SRC/system/$s" "/usr/local/bin/$s"
  echo "installed /usr/local/bin/$s"
done
echo
echo "Both are inert unless omatrix is the active theme. The ghostty one shadows"
echo "ghostty for the whole system, so it only rewrites an argument when the"
echo "invocation carries --class=org.omarchy.screensaver; everything else execs"
echo "/usr/bin/ghostty unchanged."
echo "Undo with: sudo $0 --remove"
