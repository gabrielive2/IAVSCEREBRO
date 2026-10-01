import streamlit as st
import os
import time
import random
import base64

# 1. CONFIGURACIÓN INICIAL DE LA PÁGINA WEB
st.set_page_config(page_title="IAVSCEREBRO - Quiz", layout="centered")

# =====================================================================
# CONFIGURACIÓN DE RUTAS Y CONSTANTES
# =====================================================================
FONDO_PATH = "fondo/naturaleza.jpg"
CARPETA_FACIL = "faciles"
CARPETA_INTERMEDIA = "intermedias"
CARPETA_DIFICIL = "dificiles"

IMAGENES_POR_BLOQUE = 5

# =====================================================================
# INICIALIZACIÓN DEL ESTADO DE SESIÓN (SESSION STATE)
# =====================================================================
if "fase" not in st.session_state:
    st.session_state.fase = "INICIO"
    st.session_state.modo_juego = "Modo Árbitro (Teclas V/X)"
    st.session_state.imagenes_partida = []
    st.session_state.indice_imagen = 0
    st.session_state.resultados = []  
    st.session_state.marca_tiempo_inicio = 0.0

# Función para codificar la imagen local en base64 para el fondo CSS
def obtener_base64_imagen(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# Función interna para cargar 5 imágenes aleatorias .jpg de una carpeta
def obtener_muestra_imagenes(carpeta):
    if os.path.exists(carpeta):
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.lower().endswith('.jpg')]
        if len(archivos) >= IMAGENES_POR_BLOQUE:
            return random.sample(archivos, IMAGENES_POR_BLOQUE)
        return archivos
    return []

# =====================================================================
# INTERFAZ DE USUARIO Y FLUJO DEL QUIZ
# =====================================================================

# --- PANTALLA DE INICIO (CON FONDO DE PANTALLA COMPLETO TIPO PARED) ---
if st.session_state.fase == "INICIO":
    img_base64 = obtener_base64_imagen(FONDO_PATH)
    
    if img_base64:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
                            url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
                background-size: cover !important;
            }}
            h1, p, label {{
                color: white !important;
            }}
            .stSelectbox div[data-baseweb="select"] {{
                background-color: rgba(255, 255, 255, 0.9) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"Aviso: Coloca tu imagen de fondo en la ruta para habilitar el diseño de pared: '{FONDO_PATH}'")
        
    st.title("🧠 BIENVENIDO A IAVSCEREBRO")
    st.write("Duelo de velocidad y precisión entre el cerebro humano y la inteligencia artificial.")
    
    # Selección del Modo de Juego
    st.session_state.modo_juego = st.selectbox(
        "Selecciona el modo de juego para la partida:",
        ["Modo Árbitro (Teclas V/X)", "Modo Escribir Nombre"]
    )
    
    if st.session_state.modo_juego == "Modo Árbitro (Teclas V/X)":
        st.info("🎯 **Modo Árbitro:** Presiona la tecla [V] para Acierto o [X] para Fallo directamente. Es instantáneo y pasa solo.")
    else:
        st.info("✍️ **Modo Escribir:** Escribe el nombre del animal en el cuadro inferior y presiona la tecla Enter para avanzar.")

    if st.button("🚀 Comenzar Evaluación", type="primary", use_container_width=True):
        st.session_state.fase = "PANTALLA_FACIL"
        st.rerun()

# --- PANTALLA INTERMEDIA: FÁCIL ---
elif st.session_state.fase == "PANTALLA_FACIL":
    st.subheader("🟢 Nivel Inicial")
    st.title("IMÁGENES FÁCILES")
    st.write("Prepárate para iniciar el primer bloque.")
    
    if st.button("Iniciar Bloque Fácil", use_container_width=True):
        st.session_state.imagenes_partida = obtener_muestra_imagenes(CARPETA_FACIL)
        st.session_state.indice_imagen = 0
        st.session_state.fase = "QUIZ_FACIL"
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

# --- PANTALLA INTERMEDIA: INTERMEDIO ---
elif st.session_state.fase == "PANTALLA_INTERMEDIA":
    st.subheader("🟡 Nivel Moderado")
    st.title("IMÁGENES INTERMEDIAS")
    st.write("Subiendo de nivel. La configuración y controles se mantienen iguales.")
    
    if st.button("Iniciar Bloque Intermedio", use_container_width=True):
        st.session_state.imagenes_partida = obtener_muestra_imagenes(CARPETA_INTERMEDIA)
        st.session_state.indice_imagen = 0
        st.session_state.fase = "QUIZ_INTERMEDIA"
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

# --- PANTALLA INTERMEDIA: DIFÍCIL (ADAPTABLE) ---
elif st.session_state.fase == "PANTALLA_DIFICIL":
    st.subheader("🔴 Nivel Avanzado")
    st.title("IMÁGENES DIFÍCILES")
    
    imagenes_dificiles = obtener_muestra_imagenes(CARPETA_DIFICIL)
    if not imagenes_dificiles:
        st.info("ℹ️ Bloque difícil vacío por ahora. Avanzando a la tabla de resultados finales.")
        if st.button("Ver Resultados Totales", use_container_width=True):
            st.session_state.fase = "FINAL"
            st.rerun()
    else:
        if st.button("Iniciar Bloque Difícil", use_container_width=True):
            st.session_state.imagenes_partida = imagenes_dificiles
            st.session_state.indice_imagen = 0
            st.session_state.fase = "QUIZ_DIFICIL"
            st.session_state.marca_tiempo_inicio = time.time()
            st.rerun()

# --- EJECUCIÓN DEL QUIZ ACTIVO ---
elif st.session_state.fase in ["QUIZ_FACIL", "QUIZ_INTERMEDIA", "QUIZ_DIFICIL"]:
    nivel_actual = st.session_state.fase.replace("QUIZ_", "")
    lista_actual = st.session_state.imagenes_partida
    idx = st.session_state.indice_imagen

    if idx < len(lista_actual):
        ruta_img = lista_actual[idx]
        nombre_archivo = os.path.basename(ruta_img)
        nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
        
        st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")
        st.image(ruta_img, use_container_width=True)
        
        # --- Cronómetro dinámico en segundos exactos (ej: 1.2 s) ---
        tiempo_actual = time.time()
        segundos_transcurridos = round(tiempo_actual - st.session_state.marca_tiempo_inicio, 1)
        st.markdown(f"⏱️ **Tiempo transcurrido:** `{segundos_transcurridos} s`")
        
        # CONTROLES SEGÚN EL MODO SELECCIONADO
        if st.session_state.modo_juego == "Modo Árbitro (Teclas V/X)":
            st.write("⌨️ **Presiona [V] para Acertó o [X] para Falló directamente en tu teclado**.")
            
            # Campo oculto receptor del evento Javascript
            val_receptor = st.text_input("ReceptorJS", key=f"js_rec_{st.session_state.fase}_{idx}", label_visibility="collapsed")
            
            # Script JS nativo para capturar pulsaciones instantáneas sin requerir la tecla enter
            st.components.v1.html(
                f"""
                <script>
                const doc = window.parent.document;
                function escucharTeclas(e) {{
                    let letra = e.key.toLowerCase();
                    if (letra === 'v' || letra === 'x') {{
                        doc.removeEventListener('keydown', escucharTeclas);
                        let inputs = doc.querySelectorAll('input[type="text"]');
                        if (inputs.length > 0) {{
                            let targetInput = inputs[inputs.length - 1];
                            targetInput.value = letra;
                            targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            targetInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }}
                }}
                doc.addEventListener('keydown', escucharTeclas);
                </script>
                """,
                height=0,
            )
            
            if val_receptor:
                accion = val_receptor.lower().strip()
                if accion in ['v', 'x']:
                    resultado_humano = "Acertó" if accion == 'v' else "Falló"
                    
                    # Evaluación simulada de la IA 
                    ia_achunto = random.choice(["Acertó", "Falló"])
                    tiempo_ia_s = round(segundos_transcurridos * random.uniform(0.6, 0.9), 1)
                    
                    st.session_state.resultados.append({
                        "Imagen": nombre_archivo,
                        "Nivel": nivel_actual,
                        "Tiempo Humano": f"{segundos_transcurridos} s",
                        "Humano": resultado_humano,
                        "Tiempo IA": f"{tiempo_ia_s} s",
                        "IA (Achuntó)": ia_achunto
                    })
                    
                    st.session_state.indice_imagen += 1
                    st.session_state.marca_tiempo_inicio = time.time()
                    st.rerun()

        else:
            # MODO ESCRIBIR NOMBRE DEBAJO DE LA IMAGEN
            respuesta_escrita = st.text_input("¿Qué animal es este? (Escribe el nombre y presiona Enter):", key=f"txt_{st.session_state.fase}_{idx}")
            
            if respuesta_escrita:
                if respuesta_escrita.lower().strip() == nombre_sin_ext.lower().strip():
                    resultado_humano = "Acertó"
                else:
                    resultado_humano = f"Falló (Era: {nombre_sin_ext})"
                    
                    # Evaluación simulada de la IA
                ia_achunto = random.choice(["Acertó", "Falló"])
                tiempo_ia_s = round(segundos_transcurridos * random.uniform(0.7, 0.95), 1)
st.session_state.resultados.append({
"Imagen": nombre_archivo,
"Nivel": nivel_actual,
"Tiempo Humano": f"{segundos_transcurridos} s",
"Humano": resultado_humano,
"Tiempo IA": f"{tiempo_ia_s} s",
"IA (Achuntó)": ia_achunto
})
st.session_state.indice_imagen += 1
st.session_state.marca_tiempo_inicio = time.time()
st.rerun()
# Pequeña pausa para actualizar fluidamente el contador visual en pantalla
time.sleep(0.05)
st.rerun()
if st.session_state.fase == "QUIZ_FACIL":
st.session_state.fase = "PANTALLA_INTERMEDIA"
elif st.session_state.fase == "QUIZ_INTERMEDIA":
st.session_state.fase = "PANTALLA_DIFICIL"
elif st.session_state.fase == "QUIZ_DIFICIL":
st.session_state.fase = "FINAL"
st.rerun()
--- TABLA FINAL DE METRICAS ---
elif st.session_state.fase == "FINAL":
st.title("📊 MÉTRICAS FINALES — IAVSCEREBRO")
st.success("¡Prueba concluida exitosamente!")
st.write("### Tabla Comparativa Completa")
if st.session_state.resultados:
st.table(st.session_state.resultados)
else:
st.info("No hay datos registrados en esta partida.")
if st.button("🔄 Reiniciar Nueva Evaluación", use_container_width=True):
st.session_state.clear()
st.rerun
