"""
Servidor local com suporte a atualização em tempo real da apuração do TSE.

Uso:
    python server.py
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json
import threading
import time
from atualizar_dados import coletar_dados_tse

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Desabilitar cache para todos os arquivos e habilitar CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/atualizar'):
            try:
                print("\n[TSE] Recebida solicitação de atualização ao vivo...")
                data = coletar_dados_tse()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                print("[TSE] Dados atualizados e enviados ao navegador com sucesso!\n")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        super().do_GET()

    def log_message(self, format, *args):
        msg = str(args[0]) if args else ''
        if '/api/atualizar' not in msg and '.geojson' not in msg:
            print(f"[{self.log_date_time_string()}] {msg}")

def background_updater():
    """Atualiza automaticamente em segundo plano a cada 60 segundos."""
    time.sleep(10) # aguarda servidor subir
    while True:
        try:
            print("\n[Auto-Sync] Atualizando dados em segundo plano...")
            coletar_dados_tse()
        except Exception as e:
            print(f"[Auto-Sync Erro] {e}")
        time.sleep(60)

def main():
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    
    # Iniciar thread de sincronização automática
    bg_thread = threading.Thread(target=background_updater, daemon=True)
    bg_thread.start()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 68)
        print("  MAPA ELEITORAL DO BRASIL - ELEICOES 2026 (2º TURNO AO VIVO TSE)")
        print("=" * 68)
        print(f"  Servidor ativo em: {url}")
        print("  - Disputa Presidencial: Flávio Bolsonaro (22) x Lula (13)")
        print("  - Sincronização automática em segundo plano a cada 60 segundos.")
        print("  - Pressione Ctrl+C para encerrar o servidor.")
        print("=" * 68)
        
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
            sys.exit(0)

if __name__ == "__main__":
    main()
