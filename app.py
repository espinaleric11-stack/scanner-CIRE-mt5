import base64
from io import BytesIO
from PIL import Image
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="MT5 Neural Scanner Pro", page_icon="⚡", layout="centered"
)

# Estilos CSS Futuristas / Cyberpunk con efectos de neón y terminal financiera
st.markdown(
    """
    <style>
    /* Fondo general y tipografía estilo terminal */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #080c14 0%, #010409 100%);
        color: #c9d1d9;
    }
    
    /* Títulos futuristas con brillo neón */
    h1, h2, h3 {
        font-family: 'Courier New', Courier, monospace, sans-serif;
        letter-spacing: -0.5px;
        color: #00ffcc;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
    }
    
    /* Botón cyberpunk con animación de pulso */
    div.stButton > button {
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        color: #ffffff;
        border: 1px solid #00ffcc;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        width: 100%;
        box-shadow: 0 0 15px rgba(0, 180, 216, 0.5);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.8);
        transform: translateY(-2px);
    }
    
    /* Cajas de texto y selectores personalizados */
    .stTextInput input, .stSelectbox select {
        background-color: #0d1117 !important;
        color: #00ffcc !important;
        border: 1px solid #1f6feb !important;
        border-radius: 6px !important;
    }
    
    /* Contenedor holográfico de reporte táctico */
    .report-container {
        background: rgba(13, 17, 23, 0.85);
        border: 1px solid #1f6feb;
        border-left: 4px solid #00ffcc;
        padding: 22px;
        border-radius: 8px;
        box-shadow: 0 8px 32px rgba(0, 255, 204, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado visual
st.markdown(
    "<h1 style='text-align: center;'>⚡ MT5 NEURAL TERMINAL ⚡</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #8b949e;'>Sistema autónomo"
    " institucional de análisis de price action asistido por IA</p>",
    unsafe_allow_html=True,
)
st.divider()

# Carga automática de la API Key desde los secrets de Streamlit o campo manual
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

if not api_key:
  api_key = st.text_input(
      "🔑 Introduce tu API Key de OpenRouter:",
      type="password",
      help="Clave secreta segura.",
  )

# Endpoint y modelo fijo en OpenRouter Auto
api_url = "https://openrouter.ai/api/v1/chat/completions"
modelo_sugerido = "openrouter/auto"

st.markdown(
    "🟢 **Núcleo Activo:** `openrouter/auto` (Enrutamiento inteligente de"
    " visión)"
)
st.markdown("<br>", unsafe_allow_html=True)

# Listado completo de símbolos estándar de MT5 + Índices Sintéticos
simbolos_mt5 = [
    # --- METALES ---
    "XAUUSD (Oro vs Dólar)",
    "XAGUSD (Plata vs Dólar)",
    "XPTUSD (Platino vs Dólar)",
    "XPDUSD (Paladio vs Dólar)",
    "XAUEUR (Oro vs Euro)",
    # --- FOREX: MAJORS ---
    "EURUSD (Euro / Dólar)",
    "GBPUSD (Libra / Dólar)",
    "USDJPY (Dólar / Yen Japonés)",
    "AUDUSD (Dólar Australiano / Dólar)",
    "USDCAD (Dólar / Dólar Canadiense)",
    "NZDUSD (Dólar Neozelandés / Dólar)",
    "USDCHF (Dólar / Franco Suizo)",
    # --- FOREX: CROSSES ---
    "EURGBP (Euro / Libra Esterlina)",
    "EURJPY (Euro / Yen Japonés)",
    "GBPJPY (Libra / Yen Japonés)",
    "AUDJPY (Australiano / Yen Japonés)",
    "CADJPY (Canadiense / Yen Japonés)",
    "CHFJPY (Franco / Yen Japonés)",
    "EURAUD (Euro / Australiano)",
    "EURCAD (Euro / Canadiense)",
    "EURNZD (Euro / Neozelandés)",
    "GBPAUD (Libra / Australiano)",
    "GBPCAD (Libra / Canadiense)",
    "GBPNZD (Libra / Neozelandés)",
    "AUDCAD (Australiano / Canadiense)",
    "AUDNZD (Australiano / Neozelandés)",
    "AUDCHF (Australiano / Franco)",
    "NZDCAD (Neozelandés / Canadiense)",
    "NZDCHF (Neozelandés / Franco)",
    "NZDJPY (Neozelandés / Yen)",
    "CADCHF (Canadiense / Franco)",
    "EURCHF (Euro / Franco Suizo)",
    # --- FOREX: EXOTICS ---
    "USDMXN (Dólar / Peso Mexicano)",
    "USDZAR (Dólar / Rand Sudafricano)",
    "USDTRY (Dólar / Lira Turca)",
    "USDBRL (Dólar / Real Brasileño)",
    "USDSGD (Dólar / Dólar de Singapur)",
    "USDHKD (Dólar / Dólar de Hong Kong)",
    # --- CRIPTOMONEDAS ---
    "BTCUSD (Bitcoin / Dólar)",
    "ETHUSD (Ethereum / Dólar)",
    "SOLUSD (Solana / Dólar)",
    "XRPUSD (Ripple / Dólar)",
    "BNBUSD (Binance Coin / Dólar)",
    "ADAUSD (Cardano / Dólar)",
    "DOGEUSD (Dogecoin / Dólar)",
    "LTCUSD (Litecoin / Dólar)",
    "DOTUSD (Polkadot / Dólar)",
    "LINKUSD (Chainlink / Dólar)",
    # --- ÍNDICES BURSÁTILES ---
    "US30 (Dow Jones Industrial Average)",
    "NAS100 (Nasdaq 100 Technological Index)",
    "SPX500 (S&P 500 Index)",
    "DAX40 (Alemania 40 Index)",
    "FTSE100 (Reino Unido 100 Index)",
    "CAC40 (Francia 40 Index)",
    "JP225 (Nikkei 225 - Japón)",
    "HK50 (Hang Seng - Hong Kong)",
    "AUS200 (Australia 200 Index)",
    "STOXX50 (Euro Stoxx 50)",
    # --- ÍNDICES SINTÉTICOS (Volatility, Crash/Boom, Jump, Range Break) ---
    "Volatility 10 Index (R_10)",
    "Volatility 25 Index (R_25)",
    "Volatility 50 Index (R_50)",
    "Volatility 75 Index (R_75)",
    "Volatility 100 Index (R_100)",
    "Volatility 10 (1s) Index (1HZ10V)",
    "Volatility 25 (1s) Index (1HZ25V)",
    "Volatility 50 (1s) Index (1HZ50V)",
    "Volatility 75 (1s) Index (1HZ75V)",
    "Volatility 100 (1s) Index (1HZ100V)",
    "Boom 300 Index (BOOM300)",
    "Boom 500 Index (BOOM500)",
    "Boom 1000 Index (BOOM1000)",
    "Crash 300 Index (CRASH300)",
    "Crash 500 Index (CRASH500)",
    "Crash 1000 Index (CRASH1000)",
    "Jump 10 Index (JD10)",
    "Jump 25 Index (JD25)",
    "Jump 50 Index (JD50)",
    "Jump 75 Index (JD75)",
    "Jump 100 Index (JD100)",
    "Range Break 100 Index (RBG100)",
    "Step Index (STEP)",
    # --- ENERGÍAS Y MATERIAS PRIMAS ---
    "WTI (Petróleo Crudo WTI)",
    "BRENT (Petróleo Crudo Brent)",
    "NATGAS (Gas Natural)",
    "COPPER (Cobre)",
    "SUGAR (Azúcar)",
    "COFFEE (Café)",
    "CORN (Maíz)",
    "WHEAT (Trigo)",
]

# Controles de Activo y Temporalidad
col1, col2 = st.columns(2)
with col1:
  activo_seleccionado = st.selectbox(
      "📊 Símbolo / Activo MT5", simbolos_mt5, index=0
  )
  # Extraer únicamente el ticker base (primera palabra o código entre paréntesis si aplica)
  activo = activo_seleccionado.split(" ")[0]

with col2:
  temporalidad = st.selectbox(
      "⏱️ Temporalidad",
      ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN"],
  )

archivo_imagen = st.file_uploader(
    "📁 Sube la captura de pantalla de tu gráfico MT5 (PNG, JPG)",
    type=["png", "jpg", "jpeg"],
)


def imagen_a_base64(img):
  buffered = BytesIO()
  img.save(buffered, format="PNG")
  return base64.b64encode(buffered.getvalue()).decode("utf-8")


if archivo_imagen is not None:
  imagen = Image.open(archivo_imagen)
  st.image(
      imagen,
      caption=f"Monitoreando Símbolo: {activo} [{temporalidad}]",
      use_container_width=True,
  )

  st.markdown("<br>", unsafe_allow_html=True)

  if st.button("🚀 EJECUTAR ESCANEO NEURONAL"):
    if not api_key or len(api_key) < 10:
      st.error("⚠️ Se requiere una clave de acceso válida.")
    else:
      try:
        with st.spinner(
            "🧠 Analizando geometría de mercado, liquidez y patrones..."
        ):
          imagen_base64 = imagen_a_base64(imagen)

          prompt = f"""
                    Eres un trader institucional experto en acción del precio y análisis técnico. 
                    Analiza la siguiente captura de pantalla de un gráfico de MetaTrader 5 correspondiente al activo {activo} en temporalidad {temporalidad}.

                    Proporciona un análisis estructurado exactamente con los siguientes puntos:
                    1. **Tendencia Actual:** (Alcista, Bajista o Rango).
                    2. **Zonas Clave:** Identifica soportes y resistencias relevantes visibles en el gráfico.
                    3. **Patrones / Indicadores:** Menciona si observas patrones de velas o estructura de mercado.
                    4. **Sugerencia de Entrada (Setup):** 
                       - **Dirección:** (COMPRA / VENTA / ESPERAR)
                       - **Precio de Entrada / Zona:** (Nivel aproximado)
                       - **Stop Loss (SL):** (Nivel recomendado)
                       - **Take Profit (TP):** (Nivel objetivo)
                    5. **Gestión de Riesgo:** Breve advertencia o confirmación a esperar.
                    """

          headers = {
              "Authorization": f"Bearer {api_key}",
              "Content-Type": "application/json",
              "HTTP-Referer": "https://streamlit.io",
              "X-Title": "MT5 Neural Scanner",
          }

          payload = {
              "model": modelo_sugerido,
              "messages": [{
                  "role": "user",
                  "content": [
                      {"type": "text", "text": prompt},
                      {
                          "type": "image_url",
                          "image_url": {
                              "url": f"data:image/png;base64,{imagen_base64}"
                          },
                      },
                  ],
              }],
              "max_tokens": 2048,
          }

          response = requests.post(
              api_url, headers=headers, json=payload, timeout=45
          )

          if response.status_code == 200:
            resultado_json = response.json()
            texto_respuesta = resultado_json["choices"][0]["message"][
                "content"
            ]

            st.success("✨ ¡Análisis completado con éxito!")
            st.markdown("### 📊 Reporte Táctico Institucional")

            # Contenedor con diseño futurista para el reporte
            st.markdown(
                f"<div class='report-container'>{texto_respuesta}</div>",
                unsafe_allow_html=True,
            )
          else:
            st.error(
                f"❌ Error en la conexión de red ({response.status_code}):"
                f" {response.text}"
            )

      except Exception as e:
        st.error(f"❌ Error crítico en el proceso: {e}")
