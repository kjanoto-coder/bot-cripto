import os
import requests
from flask import Flask

app = Flask(__name__)

# --- CREDENCIALES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def enviar_alerta_telegram():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[-] Faltan credenciales configuradas.")
        return

    # Mensaje estructurado con los botones apuntando a tu GitHub Pages
    mensaje = (
        "🧠 *CENTRAL DE INTELIGENCIA (GEMINI AI)*\n"
        "📊 _Analizadas: 399 altcoins de Binance (< $1 USD)_\n\n"
        "🚀 *TOP 5 GANADORAS*\n"
        "• *GTC* | $0.1481 | 🟩🟩🟩🟩🟩 | +31.2%\n"
        "  └ 📊 [Resumen IA](https://kjanoto-coder.github.io/panel-cripto/?coin=GTC&price=0.1481&change=31.2) | 🔸 [Tradear](https://www.binance.com/es/trade/GTC_USDT)\n\n"
        "⭐ *ESTADO DE TUS FAVORITAS*\n"
        "• *LUNC* | $0.00005254 (-0.2%)\n"
        "  └ 📊 [Resumen IA](https://kjanoto-coder.github.io/panel-cripto/?coin=LUNC&price=0.00005254&change=-0.2) | 🔸 [Tradear](https://www.binance.com/es/trade/LUNC_USDT)"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        resultado = response.json()
        if resultado.get("ok"):
            print("[+] Alerta enviada exitosamente a Telegram.")
        else:
            print(f"[-] Error devuelto por Telegram: {resultado}")
    except Exception as e:
        print(f"[-] Error de conexión: {e}")

@app.route("/")
def home():
    enviar_alerta_telegram()
    return "Bot de Alertas Cripto activo y operando en la nube 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
