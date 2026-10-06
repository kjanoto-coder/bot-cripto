import os
import time
import requests
import threading
from flask import Flask

# 1. Configuración del servidor web para Render
app = Flask(__name__)

@app.route('/')
def home():
    return "El bot de criptomonedas está funcionando correctamente."

# 2. Función mejorada de Telegram (con timeout de 30s y reintentos)
def enviar_alerta_telegram(mensaje):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID") 
    
    if not token or not chat_id:
        print("[-] Faltan las variables TELEGRAM_TOKEN o CHAT_ID en Render.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    # Intenta enviar el mensaje hasta 3 veces si hay microcortes
    for intento in range(3):
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("[+] Mensaje enviado a Telegram con éxito.")
                return True
            else:
                print(f"[DEBUG] Error de Telegram: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"[-] Timeout de red (Intento {intento + 1}/3). Reintentando...")
            time.sleep(2)
        except Exception as e:
            print(f"[-] Error de conexión: {e}")
            return False
            
    return False

# 3. Función para obtener el precio actual de LUNC en Binance
def obtener_precio_lunc():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=LUNCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"[-] Error obteniendo precio de Binance: {e}")
        return None

# 4. Bucle principal del Bot
def bot_loop():
    print("--- HILO DEL BOT INICIADO CORRECTAMENTE ---")
    
    # Mensaje de prueba al arrancar para confirmar que Telegram conecta bien
    enviar_alerta_telegram("🚀 *Bot de alertas iniciado en Render* 🚀\nMonitoreando LUNC/USDT.")
    
    while True:
        precio = obtener_precio_lunc()
        if precio:
            print(f"[+] Precio obtenido: {precio}")
            # Aquí irá la lógica de alertas. Por defecto, solo imprime en Render.
            # Puedes descomentar la siguiente línea si quieres que te mande el precio a Telegram:
            # enviar_alerta_telegram(f"El precio actual de LUNC es: {precio}")
        
        # Espera 15 segundos antes de volver a consultar el precio
        time.sleep(15)

if __name__ == '__main__':
    # Arranca el bucle del bot en segundo plano
    hilo_bot = threading.Thread(target=bot_loop)
    hilo_bot.daemon = True
    hilo_bot.start()
    
    # Arranca el servidor web para Render
    port =
