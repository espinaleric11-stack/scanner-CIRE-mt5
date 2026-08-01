import base64
import re
from io import BytesIO
from PIL import Image
import requests
import streamlit as st

# URL de la imagen para el fondo y la pestaña
IMAGEN_URL_FONDO_ICONO = "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=1920&auto=format&fit=crop"

# Configuración de la página
st.set_page_config(
    page_title="MT5-CIRE-SCANER", 
    page_icon="⚡", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Inicializar Historial en session_state
if "historial_scans" not in st.session_state:
    st.session_state.historial_scans = []

# Estilos CSS con Fondo de Imagen Personalizado, Gradientes y Botones de Decisión Gigantes
st.markdown(
    f"""
    <style>
    /* Fondo personalizado con imagen en la aplicación y rejilla cibernética superpuesta */
    .stApp {{
        background-color: #030712;
        background-image: 
            linear-gradient(to bottom, rgba(3, 7, 18, 0.85), rgba(3, 7, 18, 0.95)),
            url("{IMAGEN_URL_FONDO_ICONO}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #c9d1d9;
        position: relative;
        min-height: 100vh;
        padding-bottom: 140px;
    }}

    /* Contenedor fijo del trazo de electrocardiograma en movimiento al pie de página */
    .ecg-footer-bg {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        height: 100px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 L350,60 L370,20 L390,100 L410,10 L430,90 L450,60 L1200,60' fill='none' stroke='%2300ffcc' stroke-width='2' stroke-opacity='0.35'/%3E%3C/svg%3E");
        background-repeat: repeat-x;
        background-size: 1200px 100px;
        animation: ecg-footer-move 5s linear infinite;
        pointer-events: none;
        z-index: 999;
        box-shadow: 0 -5px 20px rgba(0, 255, 204, 0.1);
    }}

    @keyframes ecg-footer-move {{
        0% {{ background-position-x: 0px; }}
        100% {{ background-position-x: -1200px; }}
    }}
    
    /* Títulos futuristas con brillo neón */
    h1, h2, h3 {{
        font-family: 'Courier New', Courier, monospace, sans-serif;
        letter-spacing: -0.5px;
        color: #00ffcc;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
    }}
    
    /* Botón cyberpunk con animación de pulso */
    div.stButton > button {{
        background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        color: #ffffff;
        border: 1px solid #00ffcc;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        width: 100%;
        box-shadow: 0 0 15px rgba(0, 180, 216, 0.5);
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.8);
        transform: translateY(-2px);
    }}
    
    /* Cajas de texto y selectores personalizados con estilo translúcido */
    .stTextInput input, .stSelectbox select, .stNumberInput input {{
        background-color: rgba(13, 17, 23, 0.9) !important;
        color: #00ffcc !important;
        border: 1px solid #1f6feb !important;
        border-radius: 6px !important;
    }}
    
    /* Contenedor holográfico principal para el Setup Táctico Destacado */
    .setup-hologram {{
        background: linear-gradient(135deg, rgba(13, 17, 23, 0.95) 0%, rgba(0, 30, 40, 0.9) 100%);
        border: 2px solid #00ffcc;
        border-left: 6px solid #00ffcc;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.25), inset 0 0 15px rgba(0, 255, 204, 0.1);
        margin-bottom: 25px;
    }}

    /* Botones de acción gigantes estilo HUD Cyberpunk */
    .btn-accion-gigante {{
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        font-size: 28px;
        font-weight: 900;
        padding: 18px;
        border-radius: 12px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(0,0,0,0.6);
        text-transform: uppercase;
    }}
    .badge-compra {{
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: #030712;
        border: 2px solid #00ff66;
        text-shadow: 0 0 10px rgba(255,255,255,0.6);
    }}
    .badge-venta {{
        background: linear-gradient(135deg, #cb2d3e, #ef473a);
        color: #ffffff;
        border: 2px solid #ff3333;
        text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }}
    .badge-esperar {{
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #030712;
        border: 2px solid #ffcc00;
        text-shadow: 0 0 10px rgba(255,255,255,0.4);
    }}

    /* Clases de color dinámicas para niveles alcistas y bajistas */
    .precio-alcista {{
        color: #00ff66 !important;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 255, 102, 0.4);
    }}
    .precio-bajista {{
        color: #ff3333 !important;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 51, 51, 0.4);
    }}
    </style>

    <div class="ecg-footer-bg"></div>
    """,
    unsafe_allow_html=True,
)

# --- PANEL LATERAL: HISTORIAL DE ESCANEOS (SELECTOR DE IA OCULTO) ---
with st.sidebar:
    modelo_seleccionado = "openrouter/auto"
    
    st.markdown("### 🕒 Historial de Escaneos")
    if not st.session_state.historial_scans:
        st.info("No hay análisis previos en esta sesión.")
    else:
        for i, item in enumerate(st.session_state.historial_scans):
            if st.button(f"📌 {item['activo']} ({item['temporalidad']})", key=f"hist_{i}"):
                st.session_state["resultado_activo"] = item["resultado"]

# Encabezado principal
st.markdown("<h1 style='text-align: center;'>⚡ MT5-CIRE-SCANER ⚡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Sistema autónomo institucional de análisis de price action asistido por IA</p>", unsafe_allow_html=True)
st.divider()

# Carga segura de la API Key desde los secretos de Streamlit
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    st.error("⚠️ Falta configurar la 'OPENROUTER_API_KEY' en el archivo secrets.toml o en los secretos de Streamlit Cloud.")
    st.stop()

api_url = "https://openrouter.ai/api/v1/chat/completions"

# Listado completo de símbolos estándar de MT5 + Índices Sintéticos
simbolos_mt5 = [
    "XAUUSD (Oro vs Dólar)", "XAGUSD (Plata vs Dólar)", "XPTUSD (Platino vs Dólar)", "XPDUSD (Paladio vs Dólar)", 
    "XAUEUR (Oro vs Euro)", "EURUSD (Euro / Dólar)", "GBPUSD (Libra / Dólar)", "USDJPY (Dólar / Yen Japonés)", 
    "AUDUSD (Dólar Australiano / Dólar)", "USDCAD (Dólar / Dólar Canadiense)", "NZDUSD (Dólar Neozelandés / Dólar)", 
    "USDCHF (Dólar / Franco Suizo)", "EURGBP (Euro / Libra Esterlina)", "EURJPY (Euro / Yen Japonés)", 
    "GBPJPY (Libra / Yen Japonés)", "AUDJPY (Australiano / Yen Japonés)", "CADJPY (Canadiense / Yen Japonés)", 
    "CHFJPY (Franco / Yen Japonés)", "EURAUD (Euro / Australiano)", "EURCAD (Euro / Canadiense)", 
    "EURNZD (Euro / Neozelandés)", "GBPAUD (Libra / Australiano)", "GBPCAD (Libra / Canadiense)", 
    "GBPNZD (Libra / Neozelandés)", "AUDCAD (Australiano / Canadiense)", "AUDNZD (Australiano / Neozelandés)", 
    "AUDCHF (Australiano / Franco)", "NZDCAD (Neozelandés / Canadiense)", "NZDCHF (Neozelandés / Franco)", 
    "NZDJPY (Neozelandés / Yen)", "CADCHF (Canadiense / Franco)", "EURCHF (Euro / Franco Suizo)", 
    "USDMXN (Dólar / Peso Mexicano)", "USDZAR (Dólar / Rand Sudafricano)", "USDTRY (Dólar / Lira Turca)", 
    "USDBRL (Dólar / Real Brasileño)", "USDSGD (Dólar / Dólar de Singapur)", "USDHKD (Dólar / Dólar de Hong Kong)", 
    "BTCUSD (Bitcoin / Dólar)", "ETHUSD (Ethereum / Dólar)", "SOLUSD (Solana / Dólar)", "XRPUSD (Ripple / Dólar)", 
    "BNBUSD (Binance Coin / Dólar)", "ADAUSD (Cardano / Dólar)", "DOGEUSD (Dogecoin / Dólar)", "LTCUSD (Litecoin / Dólar)", 
    "DOTUSD (Polkadot / Dólar)", "LINKUSD (Chainlink / Dólar)", "US30 (Dow Jones Industrial Average)", 
    "NAS100 (Nasdaq 100 Technological Index)", "SPX500 (S&P 500 Index)", "DAX40 (Alemania 40 Index)", 
    "FTSE100 (Reino Unido 100 Index)", "CAC40 (Francia 40 Index)", "JP225 (Nikkei 225 - Japón)", 
    "HK50 (Hang Seng - Hong Kong)", "AUS200 (Australia 200 Index)", "STOXX50 (Euro Stoxx 50)", 
    "Volatility 10 Index (R_10)", "Volatility 25 Index (R_25)", "Volatility 50 Index (R_50)", 
    "Volatility 75 Index (R_75)", "Volatility 100 Index (R_100)", "Volatility 10 (1s) Index (1HZ10V)", 
    "Volatility 25 (1s) Index (1HZ25V)", "Volatility 50 (1s) Index (1HZ50V)", "Volatility 75 (1s) Index (1HZ75V)", 
    "Volatility 100 (1s) Index (1HZ100V)", "Boom 300 Index (BOOM300)", "Boom 500 Index (BOOM500)", 
    "Boom 1000 Index (BOOM1000)", "Crash 300 Index (CRASH300)", "Crash 500 Index (CRASH500)", 
    "Crash 1000 Index (CRASH1000)", "Jump 10 Index (JD10)", "Jump 25 Index (JD25)", "Jump 50 Index (JD50)", 
    "Jump 75 Index (JD75)", "Jump 100 Index (JD100)", "Range Break 100 Index (RBG100)", "Step Index (STEP)", 
    "WTI (Petróleo Crudo WTI)", "BRENT (Petróleo Crudo Brent)", "NATGAS (Gas Natural)", "COPPER (Cobre)", 
    "SUGAR (Azúcar)", "COFFEE (Café)", "CORN (Maíz)", "WHEAT (Trigo)"
]

# Controles de Activo y Temporalidad
col1, col2 = st.columns(2)
with col1:
    activo_seleccionado = st.selectbox("📊 Símbolo / Activo MT5", simbolos_mt5, index=0)
    activo = activo_seleccionado.split(" ")[0]

with col2:
    temporalidad = st.selectbox("⏱️ Temporalidad", ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN"])

archivo_imagen = st.file_uploader("📁 Sube la captura de pantalla de tu gráfico MT5 (PNG, JPG)", type=["png", "jpg", "jpeg"])

def imagen_a_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

if archivo_imagen is not None:
    imagen = Image.open(archivo_imagen)
    st.image(imagen, caption=f"Monitoreando Símbolo: {activo} [{temporalidad}]", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 EJECUTAR ESCANEO NEURONAL"):
        try:
            with st.spinner("🧠 Analizando geometría de mercado, liquidez y patrones..."):
                imagen_base64 = imagen_a_base64(imagen)

                prompt = f"""
                Eres un trader institucional experto en acción del precio y análisis técnico. 
                Analiza la siguiente captura de pantalla de un gráfico de MetaTrader 5 correspondiente al activo {activo} en temporalidad {temporalidad}.

                ESTRUCTURA OBLIGATORIA DE RESPUESTA (DEBE SEGUIR ESTE ORDEN EXACTO):
                1. **Sugerencia de Entrada (Setup Táctico):** (Debe ser LO PRIMERO que aparezca en el texto de respuesta).
                   - **Dirección:** (COMPRA / VENTA / ESPERAR) -> Usa exactamente una de estas palabras clave en mayúsculas.
                   - **Porcentaje de Aceptación / Probabilidad:** (Ej: 85% o el nivel de confianza técnico estimado).
                   - **Precio de Entrada / Zona:** (Nivel aproximado)
                   - **Stop Loss (SL):** (Nivel recomendado)
                   - **Take Profit (TP):** (Nivel objetivo)
                2. **Tendencia Actual:** (Alcista, Bajista o Rango).
                3. **Zonas Clave:** Identifica soportes y resistencias relevantes visibles en el gráfico.
                4. **Patrones / Indicadores:** Menciona si observas patrones de velas o estructura de mercado.
                5. **Gestión de Riesgo:** Breve advertencia o confirmación a esperar.

                INSTRUCCIÓN DE FORMATO CRÍTICA PARA LOS PRECIOS:
                - Envuelve cada valor numérico o nivel de precio alcista dentro de etiquetas HTML: <span class="precio-alcista">PRECIO</span>.
                - Envuelve cada valor numérico o nivel de precio bajista o stop loss dentro de etiquetas HTML: <span class="precio-bajista">PRECIO</span>.
                """

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://streamlit.io",
                    "X-Title": "MT5-CIRE-SCANER",
                }

                payload = {
                    "model": modelo_seleccionado,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{imagen_base64}"}},
                        ],
                    }],
                    "max_tokens": 2048,
                }

                response = requests.post(api_url, headers=headers, json=payload, timeout=45)

                if response.status_code == 200:
                    resultado_json = response.json()
                    texto_respuesta = resultado_json["choices"][0]["message"]["content"]

                    st.success("✨ ¡Análisis completado con éxito!")
                    
                    # Guardar en Historial de sesión
                    st.session_state.historial_scans.insert(0, {
                        "activo": activo,
                        "temporalidad": temporalidad,
                        "resultado": texto_respuesta
                    })
                    st.session_state["resultado_activo"] = texto_respuesta

                else:
                    st.error(f"❌ Error en la conexión de red ({response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"❌ Error crítico en el proceso: {e}")

# Mostrar el resultado actual (o el seleccionado del historial)
if "resultado_activo" in st.session_state:
    texto_res = st.session_state["resultado_activo"]
    
    # Extracción por expresión regular del porcentaje generado por la IA (ej: "85%")
    match_porcentaje = re.search(r'(\d{1,3}\s*%)', texto_res)
    porcentaje_str = match_porcentaje.group(1) if match_porcentaje else "N/D"

    # Detección inteligente de la orden operativa para el botón gigante
    texto_upper = texto_res.upper()
    if "COMPRA" in texto_upper or "BUY" in texto_upper:
        badge_html = f'<div class="btn-accion-gigante badge-compra">🟢 SEÑAL DE COMPRA (BUY) | CONFIANZA: {porcentaje_str}</div>'
    elif "VENTA" in texto_upper or "SELL" in texto_upper:
        badge_html = f'<div class="btn-accion-gigante badge-venta">🔴 SEÑAL DE VENTA (SELL) | CONFIANZA: {porcentaje_str}</div>'
    else:
        badge_html = f'<div class="btn-accion-gigante badge-esperar">🟡 MANTENER / ESPERAR (WAIT) | CONFIANZA: {porcentaje_str}</div>'

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🛰️ SETUP TÁCTICO DE ALTA PRIORIDAD", unsafe_allow_html=True)
    
    # Renderizar el botón gigante con el porcentaje incluido arriba del reporte
    st.markdown(badge_html, unsafe_allow_html=True)
    
    # Mostrar el contenido completo de la IA
    st.markdown(f"<div class='setup-hologram'>{texto_res}</div>", unsafe_allow_html=True)

    # --- CALCULADORA DE GESTIÓN DE RIESGO Y LOTAJE AVANZADA ---
    with st.expander("🧮 Calculadora de Gestión de Riesgo y Lotaje Profesional"):
        st.markdown("Calcula el tamaño de lote institucional basándose en la distancia de tu Stop Loss.")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            capital_cuenta = st.number_input("Capital Cuenta ($)", min_value=10.0, value=1000.0, step=50.0)
        with col_c2:
            porcentaje_riesgo = st.number_input("Riesgo Máximo (%)", min_value=0.1, max_value=20.0, value=1.0, step=0.1)
        with col_c3:
            distancia_sl_pips = st.number_input("Distancia Stop Loss (Pips/Puntos)", min_value=1.0, value=30.0, step=1.0)
        
        # Cálculo de dinero a arriesgar
        dinero_riesgo = capital_cuenta * (porcentaje_riesgo / 100.0)
        
        # Estimación de lotaje estándar (Asumiendo 1 lote estándar = $10 por pip para Forex mayor)
        valor_pip_estandar = 10.0 
        lote_sugerido = dinero_riesgo / (distancia_sl_pips * valor_pip_estandar)

        st.divider()
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric(label="💵 Dinero Máximo a Arriesgar", value=f"${dinero_riesgo:.2f}")
        with col_r2:
            st.metric(label="📊 Tamaño de Lote Sugerido (MT5)", value=f"{lote_sugerido:.2f} Lotes")
        
        st.caption("Nota: El cálculo de lotaje está optimizado para Forex estándar ($10/pip por lote). Si operas índices o criptos, ajusta el volumen acorde al tamaño de contrato de tu bróker en MetaTrader 5.")
