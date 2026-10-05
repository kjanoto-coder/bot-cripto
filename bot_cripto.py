import os
import ccxt
import pandas as pd
import requests

TOKEN = "8948513008:AAH-Q4ooxBQ7y0sTnccxNEaifAAKb-AxXH0"
CHAT_ID = "7864354425"
SIMBOLO = "LUNC/USDT"


class BotCriptoNube:

  def enviar_mensaje(self, texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    try:
      response = requests.post(url, json=payload, timeout=15)
      print(f">>> Código HTTP Telegram recibido: {response.status_code}")
    except Exception as e:
      print(f">>> Error al enviar mensaje a Telegram: {e}")

  def analizar_y_reportar(self):
    try:
      print(f"--- ANALIZANDO {SIMBOLO} EN BINANCE ---")
      exchange = ccxt.binance()
      ohlcv = exchange.fetch_ohlcv(SIMBOLO, timeframe="4h", limit=50)
      df = pd.DataFrame(
          ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
      )

      volumen_promedio = df["volume"].iloc[:-1].mean()
      volumen_actual = df["volume"].iloc[-1]
      precio_actual = df["close"].iloc[-1]

      mensaje = (
          f"🚀 *REPORTE NUBE 24/7 - {SIMBOLO}*\n"
          f"• Precio actual: `{precio_actual}`\n"
          f"• Volumen actual: `{volumen_actual:,.2f}`\n"
          f"• Volumen promedio: `{volumen_promedio:,.2f}`"
      )

      if volumen_actual > (volumen_promedio * 2.0):
        mensaje += (
            "\n🔥 *¡ALERTA!* Movimiento de volumen anómalo detectado. Posible"
            " acumulación o ruptura."
        )
      else:
        mensaje += "\n✅ El volumen se mantiene dentro de parámetros normales."

      self.enviar_mensaje(mensaje)
      print(">>> Reporte procesado y enviado con éxito.")

    except Exception as e:
      error_msg = f"❌ Error en la ejecución del bot: {e}"
      print(error_msg)
      self.enviar_mensaje(error_msg)


if __name__ == "__main__":
  bot = BotCriptoNube()
  bot.analizar_y_reportar()
