#!/usr/bin/env python3
"""Derive omatrix's lock from the one this machine has installed.

The theme does NOT ship a frozen LockView.qml. That file carries the password
field, the fingerprint flow and the PAM states, and a stale copy of it is the
last thing anyone wants standing between a stranger and their session. So this
starts from $OMARCHY_PATH's own LockView.qml every time and applies the
smallest change that does the job: swap what the background is.

The technique is tymurbogach's, from enter-the-matrix's lib/derive-lock.py --
deriving rather than publishing a fork, re-deriving after every update, and
aborting when the anchor no longer fits. Two things are different here:

  * The swap is CONDITIONAL. enter-the-matrix's derived lock rains under every
    theme, because a user plugin is global and it does not check which theme is
    on. This keeps Omarchy's blurred wallpaper for every other theme and shows
    the trace only while omatrix is active.

  * The password field is restyled to the box from the film, measured rather
    than eyeballed. Geometry only: nothing about what it does changes.

If an anchor does not appear exactly once, this writes nothing and leaves the
native lock alone. A half-patched lock is a machine that will not unlock.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
OMARCHY = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
SOURCE = OMARCHY / "shell/plugins/lock"
PLUGINS = HOME / ".config/omarchy/plugins"
THEME = HOME / ".config/omarchy/themes/omatrix"
USER = os.environ.get("USER") or os.environ.get("LOGNAME") or "user"
PLUGIN_ID = f"{USER}.lock"
DEST = PLUGINS / PLUGIN_ID

# TraceView.qml belongs to matrix-rain: the theme is the consumer here too.
PROVIDERS = [HOME / ".local/share/matrix-rain", Path("/usr/share/matrix-rain")]
VIEW = "TraceView.qml"


def die(msg):
    print(f"derive-lock: {msg}", file=sys.stderr)
    sys.exit(1)


def find_view():
    for p in PROVIDERS:
        f = p / "trace" / VIEW
        if f.is_file():
            return f
    die(
        "matrix-rain is not installed, so there is no trace to put on the lock.\n"
        "  git clone https://github.com/leandrolalanne/matrix-rain\n"
        "  cd matrix-rain && ./install.sh"
    )


def end_of_block(text, start):
    """Index just past the `}` that closes the block opening at `start`."""
    i = text.index("{", start)
    depth = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        elif c in "\"'":
            i += 1
            while i < len(text) and text[i] != c:
                i += 2 if text[i] == "\\" else 1
        i += 1
    die("unbalanced braces in LockView.qml")


def one_block(text, pattern, must_contain, what):
    """The single block matching `pattern` whose body contains `must_contain`."""
    hits = []
    for m in re.finditer(pattern, text, re.M):
        end = end_of_block(text, m.start())
        if must_contain in text[m.start():end]:
            hits.append((m.start(), end))
    if len(hits) != 1:
        die(
            f"expected exactly one {what} in LockView.qml, found {len(hits)}.\n"
            "  Omarchy's lock has changed shape. Leaving the native lock alone."
        )
    return hits[0]


# --- the background swap -----------------------------------------------------

GUARD = '''// Which theme is on. The same file the theme's hook and its terminal banner
// read, so all three agree without a second source of truth. Watched, so
// switching themes swaps the lock without restarting the shell.
property bool omatrixActive: false
FileView {
  path: Quickshell.env("HOME") + "/.local/state/omarchy/current/theme.name"
  watchChanges: true
  printErrors: false
  onLoaded: root.omatrixActive = text().trim().toLowerCase() === "omatrix"
  onLoadFailed: root.omatrixActive = false
}
'''

REPLACEMENT = """// omatrix puts the trace program here instead of the blurred wallpaper.
// Under every other theme the original two items below run untouched: this is a
// user plugin and it is global, so it has no business changing how anyone
// else's theme looks.
//
// `loadBackground` already meant "this view is really on screen" -- the lock
// proper, or `omarchy-shell lock preview` -- so it governs whether the trace
// runs at all. Locked it runs; on unlock it stops.
//
// Written by omatrix's scripts/derive-lock.py. Do not edit by hand: it is
// derived again from Omarchy's own LockView.qml on every update.
TraceView {
  anchors.fill: parent
  visible: root.omatrixActive
  running: root.omatrixActive && root.loadBackground
  target: root.traceTarget

  // The trace's own measured colour is a green with blue in it, at hue 159.
  // This theme is hue 108 everywhere, so the field takes the palette the rest
  // of the desktop uses. What is kept is the structure -- three tiers and a
  // peak -- because that is what the frame actually establishes; the hue is
  // the part that was only ever true of one transfer.
  dim: "#1d4a12"
  mid: "#3d9926"
  bright: "#89f76e"
  peak: "#d9ffff"
}
"""


def patch_background(text):
    img_start, img_end = one_block(
        text, r"^[ \t]*Image\s*\{", "id: wallpaper", "`Image { id: wallpaper }`")
    fx_start, fx_end = one_block(
        text, r"^[ \t]*MultiEffect\s*\{", "source: wallpaper",
        "`MultiEffect { source: wallpaper }`")
    if not img_end <= fx_start:
        die("the MultiEffect does not follow the wallpaper Image; not patching.")

    # The inserted block takes the Image's own indentation, for the same reason
    # patch_header does: a constant with four spaces baked in is wrong the day
    # Omarchy reindents the file.
    pad = re.match(r"[ \t]*", text[img_start:]).group(0)
    block = "\n".join(pad + line if line.strip() else line
                      for line in REPLACEMENT.strip("\n").splitlines()) + "\n\n"

    original = text[img_start:fx_end]
    # Both originals are kept, shown when omatrix is NOT the active theme.
    # [ \t] and not \s: \s matches newlines too, which swallowed the line break
    # after the brace and re-indented both blocks to the wrong depth.
    guarded = re.sub(r"^([ \t]*)(Image|MultiEffect)([ \t]*\{)",
                     r"\1\2\3\n\1  visible: !root.omatrixActive",
                     original, flags=re.M)
    return text[:img_start] + block + guarded + text[fx_end:]


def patch_header(text):
    """The imports and properties the swap needs.

    The indentation is taken from the line that is matched rather than assumed:
    guessing four spaces when the file uses two is how this failed the first
    time, and a file's own style is the only style that will still be right
    after Omarchy reformats something.
    """
    if "import Quickshell.Io" not in text:
        text = text.replace(
            "import QtQuick\n",
            "import QtQuick\nimport Quickshell\nimport Quickshell.Io\n", 1)

    m = re.search(r"^([ \t]*)property bool loadBackground:.*$", text, re.M)
    if not m:
        die("could not find `property bool loadBackground` to hang the guard on.")
    pad = m.group(1)
    guard = "\n".join(pad + line if line.strip() else line
                      for line in GUARD.strip("\n").splitlines())
    extra = (m.group(0) + "\n\n"
             + pad + "// What the trace resolves to. Empty until something fills it in.\n"
             + pad + 'property string traceTarget: ""\n\n'
             + guard + "\n")
    return text[:m.start()] + extra + text[m.end() + 1:]


# --- the password field, restyled to the box from the film -------------------
#
# Measured off the SYSTEM FAILURE frame, which is the same box:
#
#   473 x 61            ratio 7.75, where Omarchy's field is 5.69
#   border 3px          rgb(69,89,96) -- hue 196, 16% saturation
#   fill                rgb(6,49,37)  -- hue 163
#   text                rgb(16,154,117) -- hue 164
#   tracking            advance 1.41x the cap height, so +0.20 of pixelSize
#
# The border is the one deliberate departure: everything else in the frame sits
# at hue 159-164, and it sits at 196 with almost no saturation. It reads as
# chassis rather than as code, which is why the box does not vanish into the
# field behind it.

FIELD_PATCHES = [
    (r"readonly property int fieldWidth: \d+",
     "readonly property int fieldWidth: root.omatrixActive ? 473 : 381"),
    (r"readonly property int fieldHeight: \d+",
     "readonly property int fieldHeight: root.omatrixActive ? 61 : 67"),
    (r"readonly property int outlineThickness: \d+",
     "readonly property int outlineThickness: root.omatrixActive ? 3 : 3"),
]


def patch_placeholder(text):
    """The tracking, which is most of what makes that lettering read as it does.

    Measured: the advance is 1.41x the cap height where Courier Prime alone
    gives 1.05, so 0.20 of the pixel size has to be added. Omarchy already
    tracks the password DOTS at 0.19 of its heading size, which is as near the
    film as makes no difference -- it is only the placeholder that is untracked.

    A font property and nothing else: no geometry, no logic, no behaviour.
    """
    pattern = r"^([ \t]*)font\.pixelSize: root\.fieldFontSize$"
    hits = re.findall(pattern, text, re.M)
    if len(hits) != 1:
        die(f"expected exactly one untracked placeholder size line, found {len(hits)}.")
    return re.sub(
        pattern,
        r"\1font.pixelSize: root.fieldFontSize\n"
        r"\1font.letterSpacing: root.omatrixActive ? root.fieldFontSize * 0.20 : 0",
        text, flags=re.M)


def patch_field(text):
    for pattern, replacement in FIELD_PATCHES:
        if len(re.findall(pattern, text)) != 1:
            die(f"expected exactly one `{pattern}` in LockView.qml.")
        text = re.sub(pattern, replacement, text)
    return text


# --- writing the plugin ------------------------------------------------------


def main():
    if not (SOURCE / "LockView.qml").is_file():
        die(f"no LockView.qml under {SOURCE}")
    view = find_view()

    text = (SOURCE / "LockView.qml").read_text(encoding="utf-8")
    text = patch_header(text)
    text = patch_background(text)
    text = patch_field(text)
    text = patch_placeholder(text)

    staging = PLUGINS / f".{PLUGIN_ID}.staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    for name in ("Service.qml", "manifest.json"):
        shutil.copy2(SOURCE / name, staging / name)
    (staging / "LockView.qml").write_text(text, encoding="utf-8")
    shutil.copy2(view, staging / VIEW)

    # The same rewrite `omarchy plugin clone` does, and clonedFrom is not
    # cosmetic: the shell routes IPC aimed at the built-in id to whichever local
    # manifest declares it. Without it the session has a lock plugin that
    # nothing can reach -- including whatever asks it to lock.
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    source_id = manifest.get("id", "omarchy.lock")
    manifest["id"] = PLUGIN_ID
    manifest["name"] = "Lock Screen (omatrix)"
    om = manifest.get("omarchy") if isinstance(manifest.get("omarchy"), dict) else {}
    om["clonedFrom"] = source_id
    om.pop("clonePaths", None)
    manifest["omarchy"] = om
    (staging / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validate = shutil.which("omarchy-plugin-validate")
    if validate and subprocess.run([validate, str(staging)],
                                   capture_output=True).returncode != 0:
        shutil.rmtree(staging, ignore_errors=True)
        die("the derived plugin does not validate; leaving the native lock alone.")

    shutil.rmtree(DEST, ignore_errors=True)
    staging.rename(DEST)
    # Replacing the directory with a rename does not look like "a file was
    # saved" to the plugin watcher, so the shell keeps running the old copy.
    # Measured: the patch was in the file and the screen still showed the
    # previous one until this was asked for explicitly.
    shell = shutil.which("omarchy-shell")
    if shell:
        subprocess.run([shell, "-q", "shell", "rescanPlugins"],
                       capture_output=True, timeout=10)

    print(f"derived  {DEST}")
    print(f"         from {SOURCE}/LockView.qml")
    print(f"         trace from {view}")


if __name__ == "__main__":
    main()
