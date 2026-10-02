import streamlit as st
import os
import time
import random
import base64

st.set_page_config(page_title="IAVSCEREBRO - Quiz", layout="centered")

FONDO_PATH = "fondo/naturaleza.jpg"
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
    st.session_state.revelando_dificil = False
    st.session_state.datos_ronda_dificil = {}

def obtener_base64_imagen(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
        except Exception:
            return None
    return None

def obtener_muestra_imagenes(carpeta):
    if os.path.exists(carpeta):
        if carpeta == CARPETA_DIFICIL:
            archivos = [
                os.path.join(carpeta, f) 
                for f in os.listdir(carpeta) 
                if f.lower().endswith(('.jpg', '.jpeg')) and "_borrosa" in f.lower()
            ]
        else:
            archivos = [
                os.path.join(carpeta, f) 
                for f in os.listdir(carpeta) 
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
        st.info("🎯 **Modo Árbitro:** Evalúa las respuestas del concursante usando los botones interactivos de pantalla.")
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
        nombre_sin_ext, ext_archivo = os.path.splitext(nombre_archivo)
        
        if nivel_actual == "DIFICIL" and st.session_state.revelando_dificil:
            st.write(f"### Nivel {nivel_actual} — Solución Revelada")
            ruta_clara = ruta_img.replace("_borrosa", "_clara")
            
            if os.path.exists(ruta_clara):
                img_b64_data = obtener_base64_imagen(ruta_clara)
                if img_b64_data:
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 400px; background-color: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; margin-bottom: 20px;">
                            <img src="data:image/jpg;base64,{img_b64_data}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("No se encontró la contraparte translúcida (_clara.jpg) para esta imagen.")
                
            st.markdown(f"⏱️ **Tiempo final registrado:** `{st.session_state.datos_ronda_dificil['tiempo']}`")
            st.write(f"Humano: {st.session_state.datos_ronda_dificil['humano']} | IA: {st.session_state.datos_ronda_dificil['ia']}")
            
            if st.button("Siguiente Imagen ➡️", use_container_width=True, type="primary"):
                st.session_state.revelando_dificil = False
                st.session_state.indice_imagen += 1
                st.session_state.marca_tiempo_inicio = time.time()
                st.rerun()
                
        else:
            st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")
            
            if os.path.exists(ruta_img):
                img_b64_data = obtener_base64_imagen(ruta_img)
                if img_b64_data:
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 400px; background-color: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; margin-bottom: 20px;">
                            <img src="data:image/jpg;base64,{img_b64_data}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.error(f"No se pudo cargar la imagen en la ruta: {ruta_img}")
            
            contenedor_crono = st.empty()
            tiempo_actual = time.time()
            segundos_transcurridos = round(tiempo_actual - st.session_state.marca_tiempo_inicio, 1)
            contenedor_crono.markdown(f"⏱️ **Tiempo transcurrido:** `{segundos_transcurridos} s`")
            
            if st.session_state.modo_juego == "Modo Árbitro (Teclas V/X)":
                st.write("🎯 **Evaluación del Árbitro en tiempo real:**")
                col1, col2 = st.columns(2)
                accion = None
                
                with col1:
                    if st.button("🟩 ACERTÓ", use_container_width=True, type="primary"):
                        accion = 'v'
                with col2:
                    if st.button("🟥 FALLÓ", use_container_width=True):
                        accion = 'x'
                
                if accion in ['v', 'x']:
                    resultado_humano = "Acertó" if accion == 'v' else "Falló"
                    ia_achunto = random.choice(["Acertó", "Falló"])
                    tiempo_ia_s = round(max(0.1, segundos_transcurridos * random.uniform(0.6, 0.9)), 1)
                    
                    st.session_state.resultados.append({
                        "Imagen": nombre_archivo.replace("_borrosa", ""),
                        "Nivel": nivel_actual,
                        "Tiempo Humano": f"{segundos_transcurridos} s",
                        "Humano": resultado_humano,
                        "Tiempo IA": f"{tiempo_ia_s} s",
                        "IA (Achuntó)": ia_achunto
                    })
                    
                    if nivel_actual == "DIFICIL":
                        st.session_state.datos_ronda_dificil = {
                            "tiempo": f"{segundos_transcurridos} s",
                            "humano": resultado_humano,
                            "ia": ia_achunto
                        }
                        st.session_state.revelando_dificil = True
                        st.rerun()
                    else:
                        st.session_state.indice_imagen += 1
                        st.session_state.marca_tiempo_inicio = time.time()
                        st.rerun()
            else:
                respuesta_escrita = st.text_input("¿Qué animal es este? (Escribe el nombre y presiona Enter):", key=f"txt_{st.session_state.fase}_{idx}")
                if respuesta_escrita:
                    nombre_limpio_real = nombre_sin_ext.replace("_borrosa", "").lower().strip()
                    if respuesta_escrita.lower().strip() == nombre_limpio_real:
                        resultado_humano = "Acertó"
                    else:
                        resultado_humano = f"Falló (Era: {nombre_limpio_real})"
                    
                    ia_achunto = random.choice(["Acertó", "Falló"])
                    tiempo_ia_s = round(max(0.1, segundos_transcurridos * random.uniform(0.7, 0.95)), 1)
                    
                    st.session_state.resultados.append({
                        "Imagen": nombre_archivo.replace("_borrosa", ""),
                        "Nivel": nivel_actual,
                        "Tiempo Humano": f"{segundos_transcurridos} s",
                        "Humano": resultado_humano,
                        "Tiempo IA": f"{tiempo_ia_s} s",
                        "IA (Achuntó)": ia_achunto
                    })
                    
                    if nivel_actual == "DIFICIL":
                        st.session_state.datos_ronda_dificil = {
                            "tiempo": f"{segundos_transcurridos} s",
                            "humano": resultado_humano,
                            "ia": ia_achunto
                        }
                        st.session_state.revelando_dificil = True
                        st.rerun()
                    else:
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
        st.dataframe(st.session_state.resultados, use_container_width=True)
    else:
        st.info("No hay datos registrados en esta partida.")
        
    if st.button("🔄 Reiniciar Nueva Evaluación", use_container_width=True):
        st.session_state.clear()
        st.rerun()
