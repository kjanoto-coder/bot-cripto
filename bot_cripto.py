import os
import time
import threading
import requests
from flask import Flask

# Inicializar servidor web para cumplir con el requisito de puertos de Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot LUNC/USDT activo y funcionando 24/7 🚀"

# Credenciales desde las variables de entorno de Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(mensaje):
    """Envía un mensaje de texto plano al chat de Telegram configurado."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[-] Error: Faltan las credenciales de Telegram en las variables de entorno.")
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
    """Consulta el precio actual de LUNC usando la API pública de CoinCap."""
    url = "https://api.coincap.io/v2/assets/terra-luna-classic"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            precio_str = data.get("data", {}).get("priceUsd")
            if precio_str is not None:
                return float(precio_str)
        print(f"[-] Error al consultar CoinCap. Código HTTP: {response.status_code}")
    except Exception as e:
        print(f"[-] Excepción CoinCap: {e}")
    return None

def bucle_bot():
    """Bucle principal de ejecución continua del bot."""
    print("--- HILO DEL BOT INICIADO CORRECTAMENTE ---")
    enviar_alerta_telegram("🚀 ¡Bot LUNC iniciado y conectado correctamente en Render!")
    
    while True:
        precio = obtener_precio_lunc()
        if precio:
            mensaje = f"--- MONITOREO LUNC ---\nPrecio actual: {precio} USDT"
            print(f"[+] Precio obtenido: {precio}")
            enviar_alerta_telegram(mensaje)
        else:
            print("[-] No se pudo obtener el precio en este ciclo.")
        time.sleep(60)

if __name__ == "__main__":
    hilo_bot = threading.Thread(target=bucle_bot)
    hilo_bot.daemon = True
    hilo_bot.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
