import os
import time
import requests
from flask import Flask

app = Flask(__name__)

# --- CONFIGURACIÓN DE CREDENCIALES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print("--- INICIANDO BOT (MEXC + TELEGRAM) ---")
if TELEGRAM_TOKEN:
    # Mostramos los primeros 10 caracteres para verificar en los logs que Render lee la clave correcta
    print(f"Token configurado (primeros 10 chars): {TELEGRAM_TOKEN[:10]}...")
else:
    print("¡ADVERTENCIA! TELEGRAM_TOKEN no está configurado en las variables de entorno.")

if CHAT_ID:
    print(f"CHAT_ID configurado: {CHAT_ID}")
else:
    print("¡ADVERTENCIA! CHAT_ID no está configurado en las variables de entorno.")


def obtener_precio_mexc():
    try:
        # URL pública de la API de MEXC para el par LUNC/USDT (ajusta el par si usas otro)
        url = "https://www.mexc.com/open/api/v2/market/ticker?symbol=LUNC_USDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            precio = data["data"][0]["deal"]
            return float(precio)
    except Exception as e:
        print(f"[-] Error al consultar la API de MEXC: {e}")
    return None


def enviar_mensaje_telegram(mensaje):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[-] No se puede enviar mensaje: Faltan credenciales de Telegram.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        resultado = response.json()
        
        if resultado.get("ok"):
            print("[+] Mensaje enviado exitosamente a Telegram.")
        else:
            print(f"[-] Error de Telegram: {resultado}")
    except Exception as e:
        print(f"[-] Error de red al conectar con Telegram: {e}")


@app.route("/")
def home():
    # Realizamos una prueba rápida al entrar a la web o la ruta principal
    precio =
