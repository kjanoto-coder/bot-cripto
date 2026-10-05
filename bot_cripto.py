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

# Leer credenciales de forma segura desde las variables de entorno de Render
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
    """Consulta el precio actual de LUNC en USDT usando CoinGecko."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=terra-luna-classic&vs_currencies=usdt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            precio = data.get("terra-luna-classic", {}).get("usdt")
            if precio is not None:
                return float(precio)
        print(f"[-] Error al consultar CoinGecko. Código HTTP: {response.status_code}")
    except Exception as e:
        print(f"[-] Excepción CoinGecko: {e}")
    return None

def bucle_bot():
    """Bucle principal de ejecución continua del bot de trading."""
    print("--- HILO DEL BOT INICIADO CORRECTAMENTE ---")
    enviar_alerta_telegram("🚀 ¡Bot LUNC/USDT iniciado y conectado correctamente en Render!")
    
    while True:
        precio = obtener_precio_lunc()
        if precio:
            mensaje = f"--- MONITOREO LUNC/USDT ---\nPrecio actual: {precio} USDT"
            print(f"[+] Precio obtenido: {precio}")
            enviar_alerta_telegram(mensaje)
        else:
            print("[-] No se pudo obtener el precio en este ciclo.")
        time.sleep(60)

if __name__ == "__main__":
    # Ejecutar el bot en un hilo independiente para que no bloquee el servidor web de Flask
    hilo_bot = threading.Thread(target=bucle_bot)
    hilo_bot.daemon = True
    hilo_bot.start()

    # Iniciar Flask en el puerto asignado por Render (por defecto 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
