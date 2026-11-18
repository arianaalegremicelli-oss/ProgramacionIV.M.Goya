# escuchar.py - Herramienta de prueba de WebSocket con presencia
# Alumna: Ariana Alegre Micelli

import sys
import websocket

if len(sys.argv) < 3:
    print("Uso: python escuchar.py <proyecto_id> <token_jwt>")
    sys.exit(1)

proyecto, token = sys.argv[1], sys.argv[2]
url = f"ws://127.0.0.1:8000/ws/projects/{proyecto}/?token={token}"

try:
    ws = websocket.create_connection(url)
    print(f"Conectado al proyecto {proyecto}. Esperando eventos (Ctrl+C para salir)...")
    while True:
        mensaje = ws.recv()
        print(f"Evento recibido: {mensaje}")
except KeyboardInterrupt:
    print("\nDesconectando...")
    ws.close()
except Exception as e:
    print(f"Error de conexión WebSocket: {e}")
