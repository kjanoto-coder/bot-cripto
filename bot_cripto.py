import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot LUNC/USDT activo y funcionando 24/7 🚀"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[-] Error: Faltan las variables de entorno de Telegram.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"[DEBUG] Telegram respondió código: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] Excepción al conectar con Telegram: {e}")

def obtener_precio_lunc():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=terra-luna-classic&vs_currencies=usdt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("terra-luna-classic", {}).get("usdt", 0))
    except Exception as e:
        print(f"[-] Excepción CoinGecko: {e}")
    return None

def bucle_bot():
    print("--- HILO DEL BOT INICIADO CORRECTAMENTE ---")
    enviar_alerta_telegram("Bot LUNC iniciado en Render.")
    
    while True:
        precio = obtener_precio_lunc()
        if precio:
            mensaje = f"LUNC/USDT Precio actual: {precio}"
            print(f"[+] Precio obtenido: {precio}")
            enviar_alerta_telegram(mensaje)
        else:
            print("[-] No se pudo obtener el precio.")
        time.sleep(60)

if __name__ == "__main__":
    hilo_bot = threading.Thread(target=bucle_bot)
    hilo_bot.daemon = True
    hilo_bot.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
