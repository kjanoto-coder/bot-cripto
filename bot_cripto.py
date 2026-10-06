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
    print(f"Token configurado (primeros 10 chars): {TELEGRAM_TOKEN[:10]}...")
else:
    print("¡ADVERTENCIA! TELEGRAM_TOKEN no está configurado en las variables de entorno.")

if CHAT_ID:
    print(f"CHAT_ID configurado: {CHAT_ID}")
else:
    print("¡ADVERTENCIA! CHAT_ID no está configurado en las variables de entorno.")


def obtener_precio_mexc():
    try:
        # Endpoint actualizado de la API v3 de MEXC
        url = "https://api.mexc.com/api/v3/ticker/price?symbol=LUNCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "price" in data:
            return float(data["price"])
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
    precio = obtener_precio_mexc()
    if precio:
        mensaje_prueba = f"🤖 *Bot Cripto activo*\n📊 Precio LUNC actual: `{precio}`"
        enviar_mensaje_telegram(mensaje_prueba)
        return f"Your service is live 🚀 - Precio obtenido y enviado: {precio}"
    return "Your service is live 🚀 (No se pudo obtener el precio de MEXC)"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
