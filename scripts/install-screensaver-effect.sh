#!/bin/bash
# Install (or remove) the shim that forces the matrix screensaver effect.
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
BIN=/usr/local/bin/ttfx
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
  [[ -e $BIN ]] && { rm -f "$BIN"; echo "removed $BIN"; removed=1; }
  clear_old
  (( removed )) || echo "nothing to remove"
  exit 0
fi

[[ -x /usr/bin/ttfx ]] || { echo "/usr/bin/ttfx is missing; nothing to shim." >&2; exit 1; }

clear_old
install -Dm755 "$SRC/system/ttfx" "$BIN"
echo "installed $BIN"
echo
echo "The matrix effect is forced only while omatrix is the active theme."
echo "Undo with: sudo $0 --remove"
