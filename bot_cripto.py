import os
import time
import requests
import threading
from flask import Flask

# Servidor web básico para mantener viva la aplicación en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Activo y funcionando 🚀"

def obtener_precio_lunc():
    """Consulta el precio actual de LUNC en MEXC (evita bloqueo de Binance)"""
    try:
        url = "https://api.mexc.com/api/v3/ticker/price?symbol=LUNCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'price' in data:
            return float(data['price'])
        else:
            print(f"[-] Error del Exchange: {data}")
            return None
    except Exception as e:
        print(f"[-] Error de red obteniendo precio: {e}")
        return None

def enviar_mensaje(mensaje, token, chat_id):
    """Envía el mensaje al chat de Telegram con un tiempo de espera de 30s"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
        # Aumentamos el timeout a 30 segundos para evitar cortes por congestión
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("[+] Mensaje enviado a Telegram correctamente.")
        else:
            print(f"[-] Error de Telegram: {response.text}")
    except Exception as e:
        print(f"[-] Error de red enviando a Telegram: {e}")

def iniciar_bot():
    """Bucle principal del bot"""
    print("--- INICIANDO BOT (MEXC + TELEGRAM MEJORADO) ---")
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[-] Faltan variables TELEGRAM_TOKEN o CHAT_ID.")
        return

    while True:
        precio = obtener_precio_lunc()
        if precio is not None:
            mensaje = f"🚀 <b>Actualización de LUNC:</b>\n\nPrecio actual: <code>{precio:.8f} USDT</code>"
            print(f"[+] Precio obtenido: {precio:.8f} - Enviando mensaje a Telegram...")
            enviar_mensaje(mensaje, token, chat_id)
        
        # Espera 1 hora (3600 segundos) antes de volver a consultar
        time.sleep(3600)

if __name__ == "__main__":
    try:
        # 1. Iniciamos el bot en segundo plano
        hilo = threading.Thread(target=iniciar_bot)
        hilo.daemon = True
        hilo.start()
        
        # 2. Iniciamos el servidor web para Render
        puerto = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=puerto)
    except Exception as e:
        print(f"[-] Error fatal iniciando la app: {e}")
