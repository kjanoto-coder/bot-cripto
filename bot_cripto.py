import os
import requests

# Configuración de credenciales y URL
BASE_URL = "https://gregarious-frangollo-0346c5.netlify.app"
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")

print("🤖 Iniciando script de criptomonedas...")

def obtener_datos_binance():
    try:
        print("🔍 Conectando a la API de Binance...")
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error al conectar con Binance: {response.status_code}")
            return None
            
        tickers = response.json()
        altcoins = []
        
        for t in tickers:
            symbol = t.get('symbol', '')
            if symbol.endswith('USDT'):
                try:
                    price = float(t.get('lastPrice', 0))
                    change = float(t.get('priceChangePercent', 0))
                    volume = float(t.get('quoteVolume', 0))
                    
                    if 0 < price < 1.0:
                        altcoins.append({
                            'symbol': symbol.replace('USDT', ''),
                            'price': price,
                            'change': change,
                            'volume': volume
                        })
                except:
                    continue
                    
        if not altcoins:
            print("⚠️ No se encontraron altcoins bajo el filtro.")
            return None
            
        ganadoras = sorted(altcoins, key=lambda x: x['change'], reverse=True)[:5]
        perdedoras = sorted(altcoins, key=lambda x: x['change'])[:5]
        acumulacion = sorted(altcoins, key=lambda x: x['volume'], reverse=True)[:5]
        
        for a in acumulacion:
            a['vol_fmt'] = f"{a['volume']:,.0f}"
            
        print(f"✅ Datos obtenidos con éxito. Altcoins analizadas: {len(altcoins)}")
        return {
            'total_analizadas': len(altcoins),
            'top_ganadoras': ganadoras,
            'top_acumulacion': acumulacion,
            'top_perdedoras': perdedoras
        }
    except Exception as e:
        print(f"❌ Excepción en Binance: {e}")
        return None

def fmt_price(p):
    try:
        p_float = float(str(p).replace('$', '').replace(',', '').strip())
        if p_float < 1:
            return f"{p_float:.8f}".rstrip('0').rstrip('.')
        return f"{p_float:.2f}"
    except:
        return str(p)

def generar_mensaje(data):
    if not data:
        return "⚠️ Error: No hay datos de mercado disponibles para enviar."
        
    msg = "🧠 <b>CENTRAL DE INTELIGENCIA (GEMINI AI)</b>\n"
    msg += f"📊 Analizadas: {data['total_analizadas']} altcoins de Binance (< $1 USD)\n\n"
    
    # 1. Ganadoras
    msg += "🚀 <b>TOP 5 GANADORAS</b>\n"
    for c in data['top_ganadoras']:
        prc = fmt_price(c['price'])
        url_ia = f"{BASE_URL}/?coin={c['symbol']}&price={prc}&change={c['change']}"
        msg += f"• <b>{c['symbol']}</b> | ${prc} | 🟩🟩🟩🟩🟩 | +{c['change']:.2f}%\n"
        msg += f"  └ 📊 <a href='{url_ia}'>Resumen IA</a> | 🔶 <a href='https://www.binance.com'>Tradear</a>\n"
    msg += "\n"
    
    # 2. Acumulación
    msg += "💎 <b>TOP 5 GEMAS EN ACUMULACIÓN (< $1.00 USD)</b>\n"
    for c in data['top_acumulacion']:
        prc = fmt_price(c['price'])
        url_ia = f"{BASE_URL}/?coin={c['symbol']}&price={prc}&change={c['change']}"
        msg += f"• 🟢 <b>{c['symbol']}</b> | ${prc} | Cambio: {c['change']:.2f}% | Vol: ${c['vol_fmt']}\n"
        msg += f"  └ 📊 <a href='{url_ia}'>Resumen IA</a> | 🔶 <a href='https://www.binance.com'>Tradear</a>\n"
    msg += "\n"
    
    # 3. Perdedoras
    msg += "📉 <b>TOP 5 PERDEDORAS (Zonas de Rebote)</b>\n"
    for c in data['top_perdedoras']:
        prc = fmt_price(c['price'])
        url_ia = f"{BASE_URL}/?coin={c['symbol']}&price={prc}&change={c['change']}"
        msg += f"• <b>{c['symbol']}</b> | ${prc} | 🟥🟥🟥🟥🟥 | {c['change']:.2f}%\n"
        msg += f"  └ 📊 <a href='{url_ia}'>Resumen IA</a> | 🔶 <a href='https://www.binance.com'>Tradear</a>\n"
    msg += "\n"
    
    # 4. Favoritas
    msg += "⭐ <b>ESTADO DE TUS FAVORITAS</b>\n"
    favs = ["LUNC", "TUT", "PEPE", "SHIB", "FLOKI"]
    all_coins = {x['symbol']: x for x in (data['top_ganadoras'] + data['top_acumulacion'] + data['top_perdedoras'])}
    
    for f in favs:
        if f in all_coins:
            c = all_coins[f]
            prc = fmt_price(c['price'])
            url_ia = f"{BASE_URL}/?coin={f}&price={prc}&change={c['change']}"
            ico = "🟢" if c['change'] >= 0 else "🔴"
            msg += f"• {ico} <b>{f}</b> | ${prc} ({c['change']:.2f}%)\n"
            msg += f"  └ 📊 <a href='{url_ia}'>Resumen IA</a> | 🔶 <a href='https://www.binance.com'>Tradear</a>\n"
        else:
            url_ia = f"{BASE_URL}/?coin={f}&price=0.00&change=0"
            msg += f"• ⚪ <b>{f}</b> | Sin datos recientes\n"
            msg += f"  └ 📊 <a href='{url_ia}'>Resumen IA</a> | 🔶 <a href='#'>Tradear</a>\n"
            
    return msg

def enviar_telegram(texto):
    if not TOKEN or not CHAT_ID:
        print("❌ Faltan TELEGRAM_TOKEN o CHAT_ID en las variables de entorno.")
        return
        
    print("📤 Enviando mensaje a Telegram...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print("✅ ¡Mensaje enviado a Telegram con éxito!")
        else:
            print(f"❌ Error de Telegram ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ Excepción al conectar con Telegram: {e}")

# Ejecución directa asegurada
if __name__ == "__main__":
    datos = obtener_datos_binance()
    mensaje_final = generar_mensaje(datos)
    enviar_telegram(mensaje_final)
