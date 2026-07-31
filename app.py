import base64
from io import BytesIO
from PIL import Image
import requests
import streamlit as st

st.set_page_config(
    page_title="Escáner de Gráficos MT5 - OpenRouter",
    page_icon="📈",
    layout="centered",
)

st.title("📈 Escáner de Gráficos MT5 - OpenRouter Auto")
st.write(
    "Sube tu captura de MetaTrader 5 para recibir un análisis técnico"
    " institucional automatizado."
)

# Intentar cargar la API Key automáticamente desde st.secrets; si no existe, pedirla en pantalla
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

if not api_key:
  api_key = st.text_input(
      "Introduce tu API Key de OpenRouter:",
      type="password",
      help=(
          "Empieza por sk-or-v1-... También puedes guardarla en st.secrets para"
          " mayor comodidad."
      ),
  )

# Fijar endpoint y modelo exclusivo de OpenRouter de forma automática
api_url = "https://openrouter.ai/api/v1/chat/completions"
modelo_sugerido = "openrouter/auto"

st.info("🤖 Usando modelo inteligente de enrutamiento: **openrouter/auto**")

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


# Función auxiliar para convertir la imagen a Base64
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

  if st.button("🚀 Analizar con OpenRouter"):
    if not api_key or len(api_key) < 10:
      st.error(
          "⚠️ Por favor, introduce una API Key válida de OpenRouter para"
          " procesar la petición."
      )
    else:
      try:
        with st.spinner(
            "Enviando gráfico y conectando con OpenRouter Auto..."
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

          # Headers requeridos y recomendados por OpenRouter
          headers = {
              "Authorization": f"Bearer {api_key}",
              "Content-Type": "application/json",
              "HTTP-Referer": "https://streamlit.io",
              "X-Title": "Scanner MT5 OpenRouter",
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
