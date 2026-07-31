from PIL import Image
import google.generativeai as genai
import streamlit as st

st.set_page_config(
    page_title="Scanner de Gráficos MT5", page_icon="📈", layout="centered"
)

st.title("📈 Escáner de Gráficos MT5 con IA")
st.write(
    "Sube una captura de pantalla de tu gráfico de MetaTrader 5 para recibir un"
    " análisis técnico y una sugerencia de entrada."
)

api_key = st.text_input(
    "Introduce tu API Key de Google Gemini:",
    type="password",
    help=(
        "Obtén tu clave gratis en aistudio.google.com (empieza por AQ... o"
        " AIza...)"
    ),
)

col1, col2 = st.columns(2)
with col1:
  activo = st.text_input("Activo", value="XAUUSD")
with col2:
  temporalidad = st.selectbox(
      "Temporalidad", ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]
  )

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
    if not api_key or len(api_key) < 20:
      st.error(
          "⚠️ Por favor, introduce una API Key válida de Google Gemini (asegúrate"
          " de copiarla completa)."
      )
    else:
      try:
        with st.spinner("Analizando estructura de mercado..."):
          # Configurar la API key con la librería clásica
          genai.configure(api_key=api_key)

          # Usar el modelo estándar y compatible
          model = genai.GenerativeModel("gemini-1.5-flash")

          prompt = f"""
                    Eres un trader institucional experto en acción del precio y análisis técnico. 
                    Analiza la siguiente captura de pantalla de un gráfico de MetaTrader 5 correspondiente al activo {activo} en temporalidad {temporalidad}.

                    Proporciona un análisis estructurado exactamente con los siguientes puntos:
                    1. **Tendencia Actual:** (Alcista, Bajista o Rango).
                    2. **Zonas Clave:** Identifica visualmente soportes y resistencias relevantes visibles en el gráfico.
                    3. **Patrones / Indicadores:** Menciona si observas patrones de velas o estructura de mercado.
                    4. **Sugerencia de Entrada (Setup):** 
                       - **Dirección:** (COMPRA / VENTA / ESPERAR)
                       - **Precio de Entrada / Zona:** (Nivel aproximado)
                       - **Stop Loss (SL):** (Nivel recomendado)
                       - **Take Profit (TP):** (Nivel objetivo)
                    5. **Gestión de Riesgo:** Breve advertencia o confirmación a esperar.
                    """

          # Generar contenido enviando la imagen y el texto
          response = model.generate_content([imagen, prompt])

          st.success("¡Análisis completado!")
          st.markdown("### 📊 Reporte de Trading")
          st.markdown(response.text)

      except Exception as e:
        st.error(f"Ocurrió un error al procesar el análisis: {e}")
