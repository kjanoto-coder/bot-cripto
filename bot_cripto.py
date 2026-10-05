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

# Cargar credenciales desde las variables de entorno de Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(mensaje):
    """Envía un mensaje de texto plano al chat de Telegram configurado."""
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
        if response.status_code == 200:
            print("[+] Alerta enviada exitosamente a Telegram.")
        else:
            print(f">>> Error Telegram ({response.status_code}): {response.text}")
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
            return float(precio)
        else:
            print(f"[-] Error al consultar CoinGecko. Código HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Excepción al obtener el precio: {e}")
        return None

def bucle_bot():
    """Bucle principal de ejecución continua del bot de trading."""
    print("--- INICIANDO MONITOREO LUNC/USDT ---")
    enviar_alerta_telegram("El bot de criptomonedas se ha iniciado correctamente en Render.")
    
    while True:
        precio = obtener_precio_lunc()
        if precio:
            mensaje_analisis = f"--- ANALIZANDO LUNC/USDT ---\nPrecio actual: {precio} USDT"
            print(mensaje_analisis)
            enviar_alerta_telegram(mensaje_analisis)
        else:
            print("[-] No se pudo obtener el precio en este ciclo.")
            
        time.sleep(60)

if __name__ == "__main__":
    # Ejecutar el bot en un hilo independiente para que no bloquee el servidor web
    hilo_bot = threading.Thread(target=bucle_bot)
    hilo_bot.daemon = True
    hilo_bot.start()

    # Iniciar Flask en el puerto asignado por Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
