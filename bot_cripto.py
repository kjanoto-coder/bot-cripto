import os
import time
import random
import json
import requests
import google.generativeai as genai

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def obtener_datos_binance():
    url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al conectar con Binance: {e}")
        return []

def generar_barra_progreso(cambio, es_acumulacion=False):
    if es_acumulacion:
        return "🟨🟨🟨⬜⬜"
    if cambio > 20:
        return "🟢🟢🟢🟢🟢"
    elif cambio > 10:
        return "🟢🟢🟢🟢⬜"
    elif cambio > 5:
        return "🟢🟢🟢⬜⬜"
    elif cambio > 0:
        return "🟢🟢⬜⬜⬜"
    elif cambio > -5:
        return "🟥🟥⬜⬜⬜"
    else:
        return "🟥🟥🟥🟥🟥"

def analisis_autonomo_gemini(candidatos_resumen):
    """
    Utiliza Gemini AI de forma autónoma para evaluar el mercado y filtrar/analizar las mejores opciones.
    """
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY no configurada. Usando selección algorítmica estándar.")
        return None

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Eres un sistema autónomo de inteligencia artificial experto en trading de criptomonedas (Binance Spot).
        Analiza los siguientes datos de mercado resumidos de altcoins y selecciona inteligentemente basándote en análisis técnico, volumen, tendencia y potencial de rebote/acumulación:
        
        Datos de mercado:
        {json.dumps(candidatos_resumen, ensure_ascii=False)}
        
        Devuelve un JSON estrictamente válido con la siguiente estructura exacta (sin texto adicional fuera del JSON):
        {{
            "ganadoras": ["SIM1", "SIM2", "SIM3", "SIM4", "SIM5", "SIM6", "SIM7"],
            "acumulacion": ["SIM1", "SIM2", "SIM3", "SIM4", "SIM5", "SIM6", "SIM7"],
            "perdedoras": ["SIM1", "SIM2", "SIM3", "SIM4", "SIM5", "SIM6", "SIM7"]
        }}
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error en el análisis autónomo de Gemini AI: {e}")
        return None

def preparar_datos(tickers):
    usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT') and not any(x in t['symbol'] for x in ['UP', 'DOWN', 'BULL', 'BEAR'])]
    
    # Preparar resumen compacto para Gemini AI
    resumen_mercado = [
        {
            "symbol": t['symbol'].replace('USDT', ''),
            "price": float(t['lastPrice']),
            "change": float(t['priceChangePercent']),
            "volume": float(t['quoteVolume'])
        }
        for t in usdt_pairs
    ]
    
    # Intentar selección autónoma con Gemini AI
    seleccion_ia = analisis_autonomo_gemini(resumen_mercado[:120])
    
    if seleccion_ia and all(k in seleccion_ia for k in ['ganadoras', 'acumulacion', 'perdedoras']):
        print("¡Selección realizada de forma autónoma por Gemini AI!")
        ganadoras = [next((t for t in usdt_pairs if t['symbol'] == f"{s}USDT"), None) for s in seleccion_ia['ganadoras']]
        acumulacion = [next((t for t in usdt_pairs if t['symbol'] == f"{s}USDT"), None) for s in seleccion_ia['acumulacion']]
        perdedoras = [next((t for t in usdt_pairs if t['symbol'] == f"{s}USDT"), None) for s in seleccion_ia['perdedoras']]
        
        ganadoras = [t for t in ganadoras if t is not None][:7]
        acumulacion = [t for t in acumulacion if t is not None][:7]
        perdedoras = [t for t in perdedoras if t is not None][:7]
    else:
        # Fallback robusto
        ganadoras = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:7]
        acumulacion_pool = [t for t in usdt_pairs if float(t['lastPrice']) < 1.0]
        acumulacion = sorted(acumulacion_pool, key=lambda x: float(x['quoteVolume']), reverse=True)[:7]
        perdedoras = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']))[:7]
    
    # Tus 5 favoritas
    favoritas_simbolos = ['LUNC', 'BANK', 'BTC', 'ETH', 'SOL']
    favoritas = []
    for sim in favoritas_simbolos:
        match = next((t for t in usdt_pairs if t['symbol'] == f"{sim}USDT"), None)
        if match:
            favoritas.append(match)
            
    return ganadoras, acumulacion, perdedoras, favoritas

def construir_mensajes(ganadoras, acumulacion, perdedoras, favoritas):
    base_url_netlify = "https://gregarious-frangollo-0346c5.netlify.app"
    
    mensaje_1 = (
        "🧠 **CENTRAL DE INTELIGENCIA & GEMINI AI** (1/2)\n"
        "🤖 *Análisis Autónomo de Oportunidades de Inversión*\n"
        "⚡ **Estado:** Activo (GitHub Actions - Cada 15m)\n\n"
        "🚀 **1. TOP 7 GANADORAS (Selección IA)**\n"
    )
    
    for item in ganadoras:
        sim = item['symbol'].replace('USDT', '')
        precio = float(item['lastPrice'])
        cambio = float(item['priceChangePercent'])
        barra = generar_barra_progreso(cambio)
        unique_id = int(time.time() * 1000) + random.randint(1, 99999)
        url_ia = f"{base_url_netlify}/?coin={sim}&price={precio}&change={cambio}&v={sim}_{unique_id}"
        url_trade = f"https://www.binance.com/es/trade/{sim}_USDT"
        
        mensaje_1 += (
            f"• **{sim}** | ${precio:.8f} | {barra} | +{cambio:.1f}%\n"
            f"  └ [📊 Resumen IA]({url_ia}) | [🔶 Tradear]({url_trade})\n"
        )

    mensaje_1 += "\n💎 **2. TOP 7 ACUMULACIÓN (< $1 USD - Selección IA)**\n"
    for item in acumulacion:
        sim = item['symbol'].replace('USDT', '')
        precio = float(item['lastPrice'])
        cambio = float(item['priceChangePercent'])
        barra = generar_barra_progreso(cambio, es_acumulacion=True)
        unique_id = int(time.time() * 1000) + random.randint(1, 99999)
        url_ia = f"{base_url_netlify}/?coin={sim}&price={precio}&change={cambio}&v={sim}_{unique_id}"
        url_trade = f"https://www.binance.com/es/trade/{sim}_USDT"
        
        mensaje_1 += (
            f"• **{sim}** | ${precio:.8f} | {barra} | {cambio:+.1f}%\n"
            f"  └ [📊 Resumen IA]({url_ia}) | [🔶 Tradear]({url_trade})\n"
        )

    mensaje_2 = (
        "🧠 **CENTRAL DE INTELIGENCIA & GEMINI AI** (2/2)\n\n"
        "📉 **3. TOP 7 PERDEDORAS (Potencial Rebote - Selección IA)**\n"
    )
    for item in perdedoras:
        sim = item['symbol'].replace('USDT', '')
        precio = float(item['lastPrice'])
        cambio = float(item['priceChangePercent'])
        barra = generar_barra_progreso(cambio)
        unique_id = int(time.time() * 1000) + random.randint(1, 99999)
        url_ia = f"{base_url_netlify}/?coin={sim}&price={precio}&change={cambio}&v={sim}_{unique_id}"
        url_trade = f"https://www.binance.com/es/trade/{sim}_USDT"
        
        mensaje_2 += (
            f"• **{sim}** | ${precio:.8f} | {barra} | {cambio:.1f}%\n"
            f"  └ [📊 Resumen IA]({url_ia}) | [🔶 Tradear]({url_trade})\n"
        )

    mensaje_2 += "\n⭐ **4. TUS 5 FAVORITAS**\n"
    for item in favoritas:
        sim = item['symbol'].replace('USDT', '')
        precio = float(item['lastPrice'])
        cambio = float(item['priceChangePercent'])
        barra = generar_barra_progreso(cambio)
        unique_id = int(time.time() * 1000) + random.randint(1, 99999)
        url_ia = f"{base_url_netlify}/?coin={sim}&price={precio}&change={cambio}&v={sim}_{unique_id}"
        url_trade = f"https://www.binance.com/es/trade/{sim}_USDT"
        
        mensaje_2 += (
            f"• **{sim}** | ${precio:.8f} | {barra} | {cambio:+.1f}%\n"
            f"  └ [📊 Resumen IA]({url_ia}) | [🔶 Tradear]({url_trade})\n"
        )

    mensaje_2 += "\n✅ Análisis autónomo completado con éxito."
    
    return mensaje_1, mensaje_2

def enviar_a_telegram(mensaje_1, mensaje_2):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    p1 = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje_1,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
    
    p2 = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje_2,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
    
    if p1.status_code == 200 and p2.status_code == 200:
        print("¡Análisis autónomo enviado con éxito a Telegram!")
    else:
        print(f"Error al enviar alerta: {p1.text} | {p2.text}")

if __name__ == "__main__":
    print("Iniciando análisis autónomo con Gemini AI...")
    datos = obtener_datos_binance()
    if datos:
        ganadoras, acumulacion, perdedoras, favoritas = preparar_datos(datos)
        msg_1, msg_2 = construir_mensajes(ganadoras, acumulacion, perdedoras, favoritas)
        enviar_a_telegram(msg_1, msg_2)
