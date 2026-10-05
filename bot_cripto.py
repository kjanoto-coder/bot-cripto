import os
import time
import requests

# Cargar credenciales desde las variables de entorno de Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(mensaje):
    """Envía un mensaje de texto al chat de Telegram configurado."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[-] Error: Faltan las variables de entorno de Telegram.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[+] Alerta enviada exitosamente a Telegram.")
        else:
            print(f">>> Código HTTP Telegram recibido: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[-] Error al conectar con Telegram: {e}")

def obtener_precio_lunc():
    """Consulta el precio actual de LUNC en USDT usando la API de CoinGecko (sin restricciones geográficas)."""
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

def ejecutar_bot():
    print("--- INICIANDO MONITOREO LUNC/USDT ---")
    enviar_alerta_telegram("🚀 *El bot de criptomonedas se ha iniciado correctamente en Render.*")
    
    # Bucle principal de ejecución continua (cada 60 segundos)
    while True:
        precio = obtener_precio_lunc()
        if precio:
            mensaje_analisis = f"--- ANALIZANDO LUNC/USDT ---\nPrecio actual: `{precio} USDT`"
            print(mensaje_analisis)
            
            # Aquí puedes agregar tu lógica de indicadores técnicos y condiciones de compra/venta
            
        else:
            print("[-] No se pudo obtener el precio en este ciclo.")
            
        # Esperar 60 segundos antes de la siguiente consulta para evitar límites de la API
        time.sleep(60)

if __name__ == "__main__":
    ejecutar_bot()

if __name__ == "__main__":
  bot = BotCriptoNube()
  bot.analizar_y_reportar()
