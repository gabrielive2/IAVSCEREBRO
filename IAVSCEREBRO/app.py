import streamlit as st
import os
import time
import random
import base64

st.set_page_config(page_title="IAVSCEREBRO - Quiz", layout="centered")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = os.path.join(BASE_DIR, "fondo", "naturaleza.jpg")
CARPETA_FACIL = "faciles"
CARPETA_INTERMEDIA = "intermedias"
CARPETA_DIFICIL = "dificiles"
IMAGENES_POR_BLOQUE = 5

if "fase" not in st.session_state:
    st.session_state.fase = "INICIO"
    st.session_state.modo_juego = "Modo Árbitro (Teclas V/X)"
    st.session_state.imagenes_partida = []
    st.session_state.indice_imagen = 0
    st.session_state.resultados = []  
    st.session_state.marca_tiempo_inicio = 0.0

def obtener_base64_imagen(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except Exception:
            return None
    return None

def obtener_muestra_imagenes(carpeta):
    ruta_absoluta_carpeta = os.path.join(BASE_DIR, carpeta)
    if os.path.exists(ruta_absoluta_carpeta):
        archivos = [
            os.path.join(carpeta, f) 
            for f in os.listdir(ruta_absoluta_carpeta) 
            if f.lower().endswith(('.jpg', '.jpeg'))
        ]
        if len(archivos) >= IMAGENES_POR_BLOQUE:
            return random.sample(archivos, IMAGENES_POR_BLOQUE)
        return archivos
    return []

if st.session_state.fase == "INICIO":
    img_base64 = obtener_base64_imagen(FONDO_PATH)
    if img_base64:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("data:image/jpg;base64,{img_base64}") no-repeat center center fixed;
                background-size: cover !important;
            }}
            h1, p, label, .stMarkdown {{ color: white !important; }}
            .stSelectbox div[data-baseweb="select"] {{ background-color: rgba(255, 255, 255, 0.9) !important; }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info(f"Aviso: Para activar el fondo tipo pared, asegúrate de que exista el archivo '{FONDO_PATH}'")
        
    st.title("🧠 BIENVENIDO A IAVSCEREBRO")
    st.write("Duelo de velocidad y precisión entre el cerebro humano y la inteligencia artificial.")
    
    st.session_state.modo_juego = st.selectbox(
        "Selecciona el modo de juego para la partida:",
        ["Modo Árbitro (Teclas V/X)", "Modo Escribir Nombre"]
    )
    
    if st.session_state.modo_juego == "Modo Árbitro (Teclas V/X)":
        st.info("🎯 **Modo Árbitro:** Presiona la tecla [V] para Acierto o [X] para Fallo directamente en tu teclado.")
    else:
        st.info("✍️ **Modo Escribir:** Escribe el nombre del animal en el cuadro inferior y presiona la tecla Enter.")

    if st.button("🚀 Comenzar Evaluación", type="primary", use_container_width=True):
        st.session_state.fase = "PANTALLA_FACIL"
        st.rerun()

elif st.session_state.fase == "PANTALLA_FACIL":
    st.subheader("🟢 Nivel Inicial")
    st.title("IMÁGENES FÁCILES")
    st.write("Prepárate para iniciar el bloque de pruebas fáciles.")
    if st.button("Iniciar Bloque Fácil", use_container_width=True):
        st.session_state.imagenes_partida = obtener_muestra_imagenes(CARPETA_FACIL)
        st.session_state.indice_imagen = 0
        st.session_state.fase = "QUIZ_FACIL"
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

elif st.session_state.fase == "PANTALLA_INTERMEDIA":
    st.subheader("🟡 Nivel Moderado")
    st.title("IMÁGENES INTERMEDIAS")
    st.write("Subiendo de nivel. La configuración y los controles se mantienen iguales.")
    if st.button("Iniciar Bloque Intermedio", use_container_width=True):
        st.session_state.imagenes_partida = obtener_muestra_imagenes(CARPETA_INTERMEDIA)
        st.session_state.indice_imagen = 0
        st.session_state.fase = "QUIZ_INTERMEDIA"
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

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

elif st.session_state.fase in ["QUIZ_FACIL", "QUIZ_INTERMEDIA", "QUIZ_DIFICIL"]:
    nivel_actual = st.session_state.fase.replace("QUIZ_", "")
    lista_actual = st.session_state.imagenes_partida
    idx = st.session_state.indice_imagen

    if idx < len(lista_actual):
        ruta_img = lista_actual[idx]
        nombre_archivo = os.path.basename(ruta_img)
        nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
        
        st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")
        
        ruta_absoluta_img = os.path.join(BASE_DIR, ruta_img)
        if os.path.exists(ruta_absoluta_img):
            st.image(ruta_absoluta_img, use_container_width=True)
        else:
            st.error(f"No se pudo cargar la imagen en la ruta: {ruta_img}")
        
        tiempo_actual = time.time()
        segundos_transcurridos = round(tiempo_actual - st.session_state.marca_tiempo_inicio, 1)
        st.markdown(f"⏱️ **Tiempo transcurrido:** `{segundos_transcurridos} s`")
        
        if st.session_state.modo_juego == "Modo Árbitro (Teclas V/X)":
            st.write("⌨️ **INSTRUCCIONES DEL ÁRBITRO:**")
            st.write("🟢 Presiona **Enter** si el concursante **ACERTÓ**.")
            st.write("🔴 Presiona la barra de **Espacio** si el concursante **FALLÓ**.")
            
            entrada_arbitro = st.text_input(
                "Control Árbitro", 
                key=f"arbitro_input_{st.session_state.fase}_{idx}", 
                label_visibility="collapsed"
            )
            
            st.components.v1.html(
                f"""
                <script>
                var doc = window.parent.document;
                var inputs = doc.querySelectorAll('input[type="text"]');
                if (inputs.length > 0) {{
                    var target = inputs[inputs.length - 1];
                    target.focus();
                    target.onkeydown = function(e) {{
                        if (e.key === ' ') {{
                            target.value = 'espacio';
                        }}
                    }};
                }}
                </script>
                """,
                height=0,
            )
            
            if entrada_arbitro:
                if entrada_arbitro.strip().lower() == "espacio":
                    resultado_humano = "Falló"
                else:
                    resultado_humano = "Acertó"
                    
                ia_achunto = random.choice(["Acertó", "Falló"])
                tiempo_ia_s = round(max(0.1, segundos_transcurridos * random.uniform(0.6, 0.9)), 1)
                
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
            respuesta_escrita = st.text_input("¿Qué animal es este? (Escribe el nombre y presiona Enter):", key=f"txt_{st.session_state.fase}_{idx}")
            
            if respuesta_escrita:
                if respuesta_escrita.lower().strip() == nombre_sin_ext.lower().strip():
                    resultado_humano = "Acertó"
                else:
                    resultado_humano = f"Falló (Era: {nombre_sin_ext})"
                
                ia_achunto = random.choice(["Acertó", "Falló"])
                tiempo_ia_s = round(max(0.1, segundos_transcurridos * random.uniform(0.7, 0.95)), 1)
                
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

        time.sleep(0.1)
        st.rerun()
    else:
        if st.session_state.fase == "QUIZ_FACIL":
            st.session_state.fase = "PANTALLA_INTERMEDIA"
        elif st.session_state.fase == "QUIZ_INTERMEDIA":
            st.session_state.fase = "PANTALLA_DIFICIL"
        elif st.session_state.fase == "QUIZ_DIFICIL":
            st.session_state.fase = "FINAL"
        st.session_state.indice_imagen = 0
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

elif st.session_state.fase == "FINAL":
    st.title("📊 MÉTRICAS FINALES — IAVSCEREBRO")
    st.success("¡Prueba concluida exitosamente!")
    
    st.write("### Tabla Comparativa Completa")
    if st.session_state.resultados:
        st.table(st.seccion_state.resultados)
    else:
        st.info("no hay datos registrados en esta partida.")

    if st.button("reiniciar nueva evaluacion",use_container_widtch=true):
        st.secccion_state.clear()
        st.rerun()
