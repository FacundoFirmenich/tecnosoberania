"""Launch the local web app using a loopback-only HTTP server. No cloud or telemetry."""
from __future__ import annotations
import functools
import http.server
import os
from pathlib import Path
import sys
import threading
import webbrowser

def resource_root() -> Path:
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))

def main() -> None:
    root=resource_root()
    if not (root/'app'/'index.html').is_file():
        raise SystemExit('No se encontró app/index.html. Ejecutá desde el paquete completo.')
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
    class Server(http.server.ThreadingHTTPServer):
        allow_reuse_address=True
        daemon_threads=True
    try:
        with Server(('127.0.0.1',8765),handler) as server:
            url='http://127.0.0.1:8765/app/index.html'
            print('LaNonApp pre-alfa disponible localmente:',url)
            threading.Timer(0.35, lambda:webbrowser.open(url)).start()
            server.serve_forever()
    except OSError as ex:
        raise SystemExit('Puerto 8765 ocupado: '+str(ex))
if __name__=='__main__':main()
