import requests
import time

def enviar_alerta_telegram(mensaje, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    # Intentamos hasta 3 veces si hay un problema de red
    for intento in range(3):
        try:
            # Subimos el timeout a 30 segundos para darle margen a Render
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("[+] Mensaje enviado con éxito a Telegram.")
                return True
            else:
                print(f"[DEBUG] Telegram respondió código: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"[-] Timeout en Telegram (Intento {intento + 1}/3). Reintentando...")
            time.sleep(2) # Espera 2 segundos antes de reintentar
        except Exception as e:
            print(f"[-] Error de conexión con Telegram: {e}")
            return False
            
    print("[-] No se pudo enviar el mensaje a Telegram tras varios intentos por problemas de red.")
    return False
    
