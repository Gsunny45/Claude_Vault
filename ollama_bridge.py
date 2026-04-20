#!/usr/bin/env python3
"""
Ollama bridge — listens on 0.0.0.0:11435 and forwards to 127.0.0.1:11434
Lets Windows apps and Docker reach Ollama without sudo.
Run: python3 ~/vault/ollama_bridge.py &
"""
import socket, threading, sys

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 11434
BRIDGE_HOST = "0.0.0.0"
BRIDGE_PORT = 11435

def relay(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def handle(client):
    try:
        server = socket.create_connection((LOCAL_HOST, LOCAL_PORT), timeout=10)
        t1 = threading.Thread(target=relay, args=(client, server), daemon=True)
        t2 = threading.Thread(target=relay, args=(server, client), daemon=True)
        t1.start(); t2.start()
    except Exception as e:
        print(f"[bridge] connect failed: {e}")
        client.close()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((BRIDGE_HOST, BRIDGE_PORT))
srv.listen(64)
print(f"[bridge] 0.0.0.0:{BRIDGE_PORT} -> 127.0.0.1:{LOCAL_PORT}", flush=True)

while True:
    client, addr = srv.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()
