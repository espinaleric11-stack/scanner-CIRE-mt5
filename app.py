import os
from google import genai
from PIL import Image
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Scanner de Gráficos MT5", page_icon="📈", layout="centered"
)

st.title("📈 Escáner de Gráficos MT5 con IA")
st.write(
    "Sube una captura de pantalla de tu gráfico de MetaTrader 5 para recibir un análisis técnico rápido y una sugerencia de entrada."
)

# Intentar obtener la API key de los Secrets de Streamlit o pedirla si no existe
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
  try:
    api_key = st.secrets["GEMINI_API_KEY"]
  except:
    api_key = st.text_input(
        "Introduce tu API Key de Google Gemini:", type="password"
    )

# Selector de Activo / Temporalidad
col1, col2 = st.columns(2)
with col1:
  activo = st.text_input("Activo", value="XAUUSD")
with col2:
  temporalidad = st.selectbox(
      "Temporalidad", ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
  )

# Subir imagen
archivo_imagen = st.file_uploader(
    "Sube la captura del gráfico (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
)

if archivo_imagen is not None:
  imagen = Image.open(archivo_imagen)
  st.image(
      imagen,
      caption=f"Gráfico de {activo} ({temporalidad})",
      use_container_width=True,
  )

  if st.button("🚀 Analizar Gráfico y Dar Sugerencia"):
    if not api_key:
      st.error("Por favor, introduce tu API Key de Gemini para continuar.")
    else:
      try:
        with st.spinner("Analizando estructura de mercado y niveles clave..."):
          client = genai.Client(api_key=api_key)

          prompt = f"""
                    Eres un trader institucional experto en acción del precio y análisis técnico. 
                    Analiza la siguiente captura de pantalla de un gráfico de MetaTrader 5 correspondiente al activo {activo} en temporalidad {temporalidad}.

                    Proporciona un análisis estructurado exactamente con los siguientes puntos:
                    1. **Tendencia Actual:** (Alcista, Bajista o Rango).
                    2. **Zonas Clave:** Identifica visualmente soportes y resistencias relevantes visibles en el gráfico.
                    3. **Patrones / Indicadores:** Menciona si observas patrones de velas, estructura de mercado (rupturas, retrocesos) o comportamiento de indicadores si los hay.
                    4. **Sugerencia de Entrada (Setup):** 
                       - **Dirección:** (COMPRA / VENTA / ESPERAR)
                       - **Precio de Entrada / Zona:** (Nivel aproximado basado en la imagen)
                       - **Stop Loss (SL):** (Nivel recomendado de protección)
                       - **Take Profit (TP):** (Nivel objetivo lógico)
                    5. **Gestión de Riesgo:** Una breve advertencia sobre el riesgo o confirmación a esperar.
                    """

         response = client.models.generate_content(
              model="gemini-2.5-flash", contents=[imagen, prompt]
          )

          st.success("¡Análisis completado!")
          st.markdown("### 📊 Reporte de Trading")
          st.markdown(response.text)

      except Exception as e:
        st.error(f"Ocurrió un error al procesar el análisis: {e}")
