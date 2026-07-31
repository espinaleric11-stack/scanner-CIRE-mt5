import base64
from io import BytesIO
from PIL import Image
import requests
import streamlit as st

st.set_page_config(
    page_title="Escáner Universal de Gráficos con IA",
    page_icon="📈",
    layout="centered",
)

st.title("📈 Escáner de Gráficos MT5 - IA Universal")
st.write(
    "Sube tu gráfico y usa la API Key de cualquier proveedor compatible (OpenAI,"
    " Groq, OpenRouter, DeepSeek, etc.)."
)

# Configuración de credenciales de forma dinámica
col_k1, col_k2 = st.columns([2, 1])
with col_k1:
  api_key = st.text_input(
      "Introduce tu API Key:",
      type="password",
      help="Clave secreta de tu proveedor de IA.",
  )
with col_k2:
  proveedor = st.selectbox(
      "Proveedor / Endpoint",
      ["OpenAI", "OpenRouter", "Groq (Llama Vision)", "Personalizado"],
  )

# Definir endpoint y modelo por defecto según el proveedor seleccionado
if proveedor == "OpenAI":
  api_url = "https://api.openai.com/v1/chat/completions"
  modelo_sugerido = "gpt-4o-mini"
elif proveedor == "OpenRouter":
  api_url = "https://openrouter.ai/api/v1/chat/completions"
  modelo_sugerido = "google/gemini-2.0-flash-exp:free"
elif proveedor == "Groq (Llama Vision)":
  api_url = "https://api.groq.com/openai/v1/chat/completions"
  modelo_sugerido = "meta-llama/llama-3.2-11b-vision-instruct"
else:
  api_url = st.text_input(
      "URL de la API (Endpoint Endpoint Custom)",
      value="https://api.openai.com/v1/chat/completions",
  )
  modelo_sugerido = st.text_input("Nombre exacto del Modelo", value="gpt-4o")

if proveedor != "Personalizado":
  modelo_sugerido = st.text_input(
      "Modelo a utilizar:", value=modelo_sugerido
  )

st.divider()

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


# Función auxiliar para convertir la imagen a Base64 (compatible con APIs REST)
def imagen_a_base64(img):
  buffered = BytesIO()
  img.save(buffered, format="PNG")
  return base64.b64encode(buffered.getvalue()).decode("utf-8")


if archivo_imagen is not None:
  imagen = Image.open(archivo_imagen)
  st.image(
      imagen,
      caption=f"Gráfico de {activo} ({temporalidad})",
      use_container_width=True,
  )

  if st.button("🚀 Analizar con IA Universal"):
    if not api_key or len(api_key) < 10:
      st.error(
          "⚠️ Por favor, introduce una API Key válida para procesar la"
          " petición."
      )
    else:
      try:
        with st.spinner(
            "Enviando gráfico y conectando con el proveedor de IA..."
        ):
          # Convertir imagen a base64 para envío HTTP estándar
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

          # Estructura de payload estándar compatible con OpenAI, Groq, OpenRouter, etc.
          headers = {
              "Authorization": f"Bearer {api_key}",
              "Content-Type": "application/json",
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
              "max_tokens": 1000,
          }

          # Petición HTTP POST universal
          response = requests.post(
              api_url, headers=headers, json=payload, timeout=30
          )

          if response.status_code == 200:
            resultado_json = response.json()
            texto_respuesta = resultado_json["choices"][0]["message"][
                "content"
            ]

            st.success("¡Análisis completado con éxito!")
            st.markdown("### 📊 Reporte de Trading")
            st.markdown(texto_respuesta)
          else:
            st.error(
                f"Error en la API ({response.status_code}):"
                f" {response.text}"
            )

      except Exception as e:
        st.error(f"Ocurrió un error al procesar la solicitud: {e}")
