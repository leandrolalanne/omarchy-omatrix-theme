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
BIN=/usr/local/bin/omarchy-screensaver
LIB=/usr/local/libexec/omatrix

(( EUID == 0 )) || { echo "This one needs root: sudo $0 $*" >&2; exit 1; }

if [[ ${1:-} == --remove ]]; then
  removed=0
  [[ -e $BIN ]] && { rm -f "$BIN"; echo "removed $BIN"; removed=1; }
  [[ -d $LIB ]] && { rm -rf "$LIB"; echo "removed $LIB"; removed=1; }
  (( removed )) || echo "nothing to remove"
  exit 0
fi

[[ -x /usr/bin/omarchy-screensaver ]] || {
  echo "/usr/bin/omarchy-screensaver is missing; nothing to shim." >&2; exit 1; }

install -Dm755 "$SRC/system/omarchy-screensaver" "$BIN"
install -Dm755 "$SRC/system/libexec/ttfx" "$LIB/ttfx"
echo "installed $BIN"
echo "installed $LIB/ttfx"
echo
echo "The matrix effect is forced only while omatrix is the active theme."
echo "Undo with: sudo $0 --remove"
