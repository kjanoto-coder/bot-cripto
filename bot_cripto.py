import os
import time
import requests
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Activo 🚀"

def obtener_precio_lunc():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=LUNCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        else:
            print(f"[-] Error Binance: {data}")
            return None
    except Exception as e:
        print(f"[-] Error de red: {e}")
        return None

def enviar_mensaje(mensaje, token, chat_id):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[-] Error enviando a Telegram: {e}")

def iniciar_bot():
    print("--- INICIANDO BOT ---")
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[-] Faltan variables TELEGRAM_TOKEN o CHAT_ID.")
        return

    while True:
        precio = obtener_precio_lunc()
        if precio is not None:
            mensaje = f"🚀 <b>LUNC:</b> <code>{precio:.8f} USDT</code>"
            print(f"[+] Enviando precio: {precio:.8f}")
            enviar_mensaje(mensaje, token, chat_id)
        
        # Espera 1 hora (3600 segundos) antes de volver a consultar
        time.sleep(3600)

if __name__ == "__main__":
    try:
        # Iniciamos el bot en segundo plano
        hilo = threading.Thread(target=iniciar_bot)
        hilo.daemon = True
        hilo.start()
        
        # Iniciamos el servidor web para mantener viva la app
        puerto = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=puerto)
    except Exception as e:
        print(f"[-] Error fatal iniciando la app: {e}")
