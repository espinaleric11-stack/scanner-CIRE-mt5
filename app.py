from google import genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Scanner de Gráficos MT5", page_icon="📈", layout="centered"
)

st.title("📈 Escáner de Gráficos MT5 con IA")

# Campo directo en pantalla para evitar errores de secretos
api_key = st.text_input(
    "Introduce tu API Key de Google Gemini:",
    type="password",
    help=(
        "Obtén tu clave gratis en aistudio.google.com (empieza por AIza...)"
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

 # Botón para iniciar el análisis
  if st.button("🚀 Analizar Gráfico y Dar Sugerencia"):
    # Verificamos que exista algo escrito, pero quitamos la regla estricta de "AIza"
    if not api_key or len(api_key) < 20:
      st.error(
          "⚠️ Por favor, introduce una API Key válida de Google Gemini (asegúrate"
          " de copiarla completa sin espacios)."
      )
    else:
      try:
        with st.spinner("Analizando estructura de mercado..."):
          # Inicializar el cliente con la clave proporcionada
          client = genai.Client(api_key=api_key)

          # Definir el prompt (las instrucciones para la IA)
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

          # Llamada al modelo (gemini-2.5-flash es el más rápido y capaz)
response = client.models.generate_content(
    model="gemini-1.5-flash", contents=[imagen, prompt] # Cambia el modelo aquí
))

          # Mostrar resultados
          st.success("¡Análisis completado!")
          st.markdown("### 📊 Reporte de Trading")
          st.markdown(response.text)

      except Exception as e:
        st.error(f"Ocurrió un error al procesar el análisis: {e}")
