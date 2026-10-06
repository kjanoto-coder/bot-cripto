import os
import time
import requests
import threading
from flask import Flask

# Inicializamos la aplicación Flask para que Render mantenga el servicio activo
app = Flask(__name__)

@app.route('/')
def home():
    return "Your service is live 🚀"

def obtener_precio_lunc():
    """Consulta el precio actual de LUNC en Binance"""
    try:
        # Buscamos específicamente LUNCUSDT
        url = "https://api.binance.com/api/v3/ticker/price?symbol=LUNCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Validamos que la respuesta contenga 'price'
        if 'price' in data:
            return float(data['price'])
        else:
            print(f"[-] Binance respondió con algo inesperado: {data}")
            return None
            
    except Exception as e:
        print(f"[-] Error de red al consultar Binance: {e}")
        return None

def enviar_mensaje_telegram(mensaje, token, chat_id):
    """Envía el mensaje al chat de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("[+] Mensaje enviado a Telegram con éxito.")
        else:
            print(f"[-] Error enviando a Telegram: {response.text}")
    except Exception as e:
        print(f"[-] Error de conexión con Telegram: {e}")

def iniciar_bot():
    """Bucle principal del bot que se ejecutará en segundo plano"""
    print("--- HILO DEL BOT INICIADO CORRECTAMENTE ---")
    
    # Obtenemos las variables de entorno configuradas en Render
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    # Si falta alguna variable, avisamos y detenemos este hilo
    if not token or not chat_id:
        print("[-] Faltan las variables TELEGRAM_TOKEN o CHAT_ID en Render.")
        return

    # Bucle infinito del bot
    while True:
        precio = obtener_precio_lunc()
        
        if precio is not None:
            # Formateamos el precio con 8 decimales por ser una criptomoneda de valor pequeño
            mensaje = f"🚀 <b>Actualización de Precio</b>\n\nEl precio de <b>LUNC</b> es: <code>{precio:.8f} USDT</code>"
            print(f"[+] Precio obtenido: {precio:.8f} - Enviando mensaje...")
            
            enviar_mensaje_telegram(mensaje, token, chat_id)
        
        # Tiempo de espera antes de volver a consultar (3600 segundos = 1 hora)
        # Puedes cambiar este número si quieres que av
