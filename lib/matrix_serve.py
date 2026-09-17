"""Servidor HTTP local para servir la copia vendorizada de Rezmason/matrix.

Existe porque `index.html` de upstream carga `<script type="module">` y los
navegadores bloquean modulos ES sobre `file://` por CORS. El propio README de
upstream sugiere `python3 -m http.server`; esto es lo mismo con dos agregados:

- inyecta un script nuestro en el HTML al vuelo, asi `vendor/matrix/` queda
  identico a upstream y actualizarlo es reemplazar el directorio;
- expone `/__exit`, porque una pagina web no puede matar su propio proceso.
  El screensaver lo usa para salir ante input. El fondo no lo usa.

Lo consumen `bin/matrix-serve` (CLI, para el screensaver) y
`background/bin/matrix-background` (lo importa y lo corre en un hilo).
"""

import http.server
import socketserver
import threading
import urllib.parse
from pathlib import Path

INJECT_MARKER = b"</body>"


def build_handler(root: Path, overlay: Path | None, on_exit=None, on_ready=None):
    """Devuelve una clase handler configurada para estas rutas."""

    inject_tag = b'<script src="/__overlay/exit.js"></script>\n\t</body>'

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

        def log_message(self, fmt, *args):  # silencio: corre detras de un fondo
            pass

        def _no_content(self):
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            path = self.path.split("?", 1)[0]

            if path == "/__exit":
                self._no_content()
                reason = urllib.parse.parse_qs(self.path.partition("?")[2]).get("reason", ["?"])[0]
                if on_exit:
                    on_exit(reason)
                return

            if path == "/__ready":
                self._no_content()
                if on_ready:
                    on_ready()
                return

            if path.startswith("/__overlay/"):
                return self._serve_overlay(path[len("/__overlay/"):])

            if path in ("/", "/index.html"):
                return self._serve_index()

            return super().do_GET()

        def _send_bytes(self, body, content_type):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _serve_overlay(self, name):
            # overlay/ es plano: ni subdirectorios ni travesia.
            if overlay is None:
                self.send_error(404)
                return
            candidate = (overlay / name).resolve()
            if candidate.parent != overlay.resolve() or not candidate.is_file():
                self.send_error(404)
                return
            self._send_bytes(candidate.read_bytes(), "application/javascript; charset=utf-8")

        def _serve_index(self):
            body = (root / "index.html").read_bytes()
            # Sin overlay (el caso del fondo) el HTML va tal cual.
            if overlay is not None:
                if INJECT_MARKER in body:
                    body = body.replace(INJECT_MARKER, inject_tag, 1)
                else:
                    body += inject_tag
            self._send_bytes(body, "text/html; charset=utf-8")

    return Handler


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve(root, overlay=None, port=0, on_exit=None, on_ready=None):
    """Arranca el servidor en un hilo. Devuelve (httpd, puerto)."""
    root = Path(root).resolve()
    overlay = Path(overlay).resolve() if overlay else None
    if not root.is_dir():
        raise NotADirectoryError(f"root no es un directorio: {root}")
    if overlay is not None and not overlay.is_dir():
        raise NotADirectoryError(f"overlay no es un directorio: {overlay}")

    httpd = Server(("127.0.0.1", port), build_handler(root, overlay, on_exit, on_ready))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def build_query(params):
    """Convierte un dict de parametros en query string para Rezmason."""
    return urllib.parse.urlencode(params)


def read_conf(path, into=None):
    """Lee un .conf de `clave=valor` con `#` como comentario."""
    params = {} if into is None else into
    try:
        text = Path(path).read_text()
    except OSError:
        return params
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        params[key.strip()] = value.strip()
    return params
