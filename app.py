import base64
from io import BytesIO
from PIL import Image
import requests
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="MT5 Neural Scanner", page_icon="⚡", layout="centered"
)

# Estilos CSS Futuristas / Cyberpunk
st.markdown(
    """
    <style>
    /* Fondo general y tipografía */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1117 0%, #010409 100%);
        color: #c9d1d9;
    }
    
    /* Títulos futuristas */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
        color: #58a6ff;
        text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
    }
    
    /* Botón futurista */
    div.stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border: 1px solid #3fb950;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 0 25px rgba(63, 185, 80, 0.8);
        transform: translateY(-2px);
    }
    
    /* Cajas de texto y selectores */
    .stTextInput input, .stSelectbox select {
        background-color: #161b22 !important;
        color: #58a6ff !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    
    /* Tarjeta de reporte */
    .report-container {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363d;
        border-left: 4px solid #58a6ff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado visual
st.markdown(
    "<h1 style='text-align: center;'>⚡ MT5 NEURAL SCANNER ⚡</h1>",
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

# Lista completa de activos organizados por categorías
activos_financieros = [
    # Metales
    "XAUUSD (Oro)",
    "XAGUSD (Plata)",
    "XPTUSD (Platino)",
    "XPDUSD (Paladio)",
    # Forex Majors
    "EURUSD (Euro / Dólar)",
    "GBPUSD (Libra / Dólar)",
    "USDJPY (Dólar / Yen)",
    "AUDUSD (Dólar Australiano)",
    "USDCAD (Dólar / Dólar Canadiense)",
    "NZDUSD (Dólar Neozelandés)",
    "USDCHF (Dólar / Franco Suizo)",
    # Forex Minors / Crosses
    "EURGBP (Euro / Libra)",
    "EURJPY (Euro / Yen)",
    "GBPJPY (Libra / Yen)",
    "AUDJPY (Australiano / Yen)",
    # Criptomonedas
    "BTCUSD (Bitcoin)",
    "ETHUSD (Ethereum)",
    "SOLUSD (Solana)",
    "XRPUSD (Ripple)",
    # Índices Bursátiles
    "US30 (Dow Jones)",
    "NAS100 (Nasdaq)",
    "SPX500 (S&P 500)",
    "DAX40 (Alemania)",
    # Materias Primas / Energía
    "WTI (Petróleo Crudo)",
    "BRENT (Petróleo Brent)",
    "NATGAS (Gas Natural)",
]

# Controles de Activo y Temporalidad
col1, col2 = st.columns(2)
with col1:
  activo_seleccionado = st.selectbox(
      "📊 Seleccionar Activo / Par", activos_financieros, index=0
  )
  # Extraer únicamente el ticker base (ej: "XAUUSD" de "XAUUSD (Oro)")
  activo = activo_seleccionado.split(" ")[0]

with col2:
  temporalidad = st.selectbox(
      "⏱️ Temporalidad", ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]
  )

archivo_imagen = st.file_uploader(
    "📁 Sube la captura de pantalla de tu gráfico (PNG, JPG)",
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
      caption=f"Monitoreando: {activo} [{temporalidad}]",
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
