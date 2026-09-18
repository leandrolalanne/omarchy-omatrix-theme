import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick

// The machinery. It renders nothing of its own: the rain, its shaders and its
// atlases all come from the matrix-rain provider, which this only mounts.
//
// Selecting a wallpaper named `<NN>-<version>.live.webp` turns it on, and the
// version is read out of that filename -- the provider declares the convention
// in its provider.json and this is the other half of it. Any other wallpaper
// leaves the surface hidden and the static image showing, so a theme that ships
// none of those costs nothing.
//
// It sits on WlrLayer.Bottom, above the wallpaper and below ordinary windows,
// with an empty input region so clicks fall straight through. It is a plugin of
// its own rather than a fork of omarchy.background, so the stock renderer keeps
// working and a mistake here cannot leave the desktop black.
Item {
  id: root

  // Where matrix-rain's install.sh puts the provider, then a system-wide copy.
  readonly property var providerDirs: [
    Quickshell.env("HOME") + "/.local/share/matrix-rain",
    "/usr/share/matrix-rain"
  ]

  property string providerDir: ""
  property string version: ""
  readonly property bool live: version !== "" && providerDir !== ""

  // `<NN>-<version>.live.webp` -> `<version>`. Anything without the marker is
  // not ours: enter-the-matrix watches for `-live-`, and both can be installed.
  function versionFromPath(path) {
    var base = path.substring(path.lastIndexOf("/") + 1)
    var cut = base.indexOf(".live.")
    if (cut < 0)
      return ""
    return base.substring(0, cut).replace(/^\d+-/, "")
  }

  Process {
    id: locate
    command: ["bash", "-lc",
      'for d in "$HOME/.local/share/matrix-rain" /usr/share/matrix-rain; do ' +
      '[ -f "$d/qml/MatrixRain.qml" ] && { printf %s "$d"; exit 0; }; done']
    stdout: StdioCollector {
      onStreamFinished: {
        root.providerDir = text.trim()
        if (root.providerDir === "")
          console.log("omatrix: the matrix-rain provider is not installed;" +
                      " live backgrounds stay off. See github.com/leandrolalanne/matrix-rain")
      }
    }
  }

  // Omarchy publishes the current background as a symlink and updates it in
  // place, which inotify on the path does not reliably report -- so this polls,
  // the way the stock background plugin does. The IPC below is what makes a
  // switch feel immediate; the poll is the floor under it.
  Process {
    id: probe
    command: ["readlink", "-f", Quickshell.env("HOME") + "/.local/state/omarchy/current/background"]
    stdout: StdioCollector {
      onStreamFinished: root.version = root.versionFromPath(text.trim())
    }
  }

  Timer {
    interval: 2000
    repeat: true
    running: true
    triggeredOnStart: true
    onTriggered: probe.running = true
  }

  IpcHandler {
    target: "omatrix"
    function refresh(): void { probe.running = true }
  }

  Component.onCompleted: locate.running = true

  Variants {
    model: Quickshell.screens

    PanelWindow {
      required property var modelData

      screen: modelData
      anchors { top: true; bottom: true; left: true; right: true }
      color: "transparent"
      visible: root.live

      WlrLayershell.namespace: "omatrix-background"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
      exclusionMode: ExclusionMode.Ignore
      mask: Region {}

      // The provider's own component, loaded from where it is installed. Its
      // shaders and atlases resolve relative to that file, so pointing at it is
      // the whole integration -- nothing here needs to know their paths.
      Loader {
        id: rain
        anchors.fill: parent
        active: root.live
        source: root.live ? "file://" + root.providerDir + "/qml/MatrixRain.qml" : ""

        // A wallpaper is not an entrance: the intro would replay on every
        // reload and every screen change.
        onLoaded: item.skipIntro = true
      }

      // The rain is a pure function of time, so switching version needs no
      // restart -- the new parameters take effect on the next frame. A binding
      // rather than an assignment in onLoaded, which would only ever fire once.
      Binding {
        target: rain.item
        property: "version"
        value: root.version
        when: rain.item !== null
      }
    }
  }
}
