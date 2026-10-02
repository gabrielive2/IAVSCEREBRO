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

defaults = {
    "fase": "INICIO",
    "modo_juego": "Modo Alternativas (A, B, C, D)",
    "imagenes_partida": [],
    "indice_imagen": 0,
    "resultados": [],  
    "marca_tiempo_inicio": 0.0,
    "opciones_actuales": [],
    "respuesta_correcta": "",
    "respondido": False,
    "resultado_ronda": {},
    "ultima_idx": -1
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

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
        st.info(f"Aviso: Asegúrate de que exista el archivo '{FONDO_PATH}' para el fondo.")
        
    st.title("🧠 BIENVENIDO A IAVSCEREBRO")
    st.write("Duelo de velocidad y precisión entre el cerebro humano y la inteligencia artificial.")
    
    st.session_state.modo_juego = st.selectbox(
        "Selecciona el modo de juego para la partida:",
        ["Modo Alternativas (A, B, C, D)", "Modo Escribir Nombre"]
    )
    
    if st.session_state.modo_juego == "Modo Alternativas (A, B, C, D)":
        st.info("🎯 **Modo Alternativas:** Haz clic en la opción correcta (A, B, C o D).")
    else:
        st.info("✍️ **Modo Escribir:** Escribe el nombre del animal en el cuadro de texto y presiona Enter.")

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
    st.write("Subiendo de nivel. Prepárate para el siguiente reto.")
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
        
        if st.session_state.ultima_idx != idx and st.session_state.modo_juego == "Modo Alternativas (A, B, C, D)":
            carpeta_map = {"FACIL": CARPETA_FACIL, "INTERMEDIA": CARPETA_INTERMEDIA, "DIFICIL": CARPETA_DIFICIL}
            carpeta_obj = carpeta_map.get(nivel_actual, CARPETA_FACIL)
            
            todos_archivos = [f for f in os.listdir(carpeta_obj) if f.lower().endswith(('.jpg', '.jpeg'))]
            nombres_pool = []
            for f in todos_archivos:
                n = os.path.splitext(f)[0].replace("_borrosa", "").replace("_clara", "").replace("_", " ").title()
                if n not in nombres_pool:
                    nombres_pool.append(n)
            
            nombre_correcto = os.path.splitext(nombre_archivo)[0].replace("_borrosa", "").replace("_clara", "").replace("_", " ").title()
            distractores = [n for n in nombres_pool if n.lower() != nombre_correcto.lower()]
            random.shuffle(distractores)
            
            opciones = distractores[:3] + [nombre_correcto] if len(distractores) >= 3 else distractores + [nombre_correcto]
            while len(opciones) < 4 and len(nombres_pool) > len(opciones):
                extra = random.choice(nombres_pool)
                if extra not in opciones:
                    opciones.append(extra)
            random.shuffle(opciones)
            
            st.session_state.opciones_actuales = opciones
            st.session_state.respuesta_correcta = nombre_correcto
            st.session_state.ultima_idx = idx
            st.session_state.respondido = False

        st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")
        
        if os.path.exists(ruta_img):
            img_b64_data = obtener_base64_imagen(ruta_img)
            if img_b64_data:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 380px; background-color: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; margin-bottom: 15px;">
                        <img src="data:image/jpg;base64,{img_b64_data}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.error(f"No se pudo cargar la imagen en la ruta: {ruta_img}")
        
        # Cronizador dinámico sin bloqueos
        tiempo_actual = time.time()
        segundos_transcurridos = round(tiempo_actual - st.session_state.marca_tiempo_inicio, 1)
        st.markdown(f"⏱️ **Tiempo transcurrido:** `{segundos_transcurridos} s`")
        
        letras = ["a", "b", "c", "d"]
        
        def procesar_respuesta(op_seleccionada):
            es_correcto = (op_seleccionada.lower().strip() == st.session_state.respuesta_correcta.lower().strip())
            resultado_humano = "Acertó" if es_correcto else f"Falló (Era: {st.session_state.respuesta_correcta})"
            
            ia_achunto = random.choice(["Acertó", "Falló"])
            tiempo_ia_s = round(max(0.1, segundos_transcurridos * random.uniform(0.6, 0.9)), 1)
            
            st.session_state.resultados.append({
                "Imagen": nombre_archivo.replace("_borrosa", "").replace("_clara", ""),
                "Nivel": nivel_actual,
                "Tiempo Humano": f"{segundos_transcurridos} s",
                "Humano": resultado_humano,
                "Tiempo IA": f"{tiempo_ia_s} s",
                "IA (Achuntó)": ia_achunto
            })
            
            st.session_state.respondido = True
            st.session_state.resultado_ronda = {
                "es_correcto": es_correcto,
                "humano": resultado_humano,
                "ia": ia_achunto,
                "tiempo": f"{segundos_transcurridos} s"
            }
            st.rerun()

        if st.session_state.modo_juego == "Modo Alternativas (A, B, C, D)":
            if not st.session_state.respondido:
                st.write("🎯 **Selecciona la alternativa correcta:**")
                cols = st.columns(2)
                for i, op in enumerate(st.session_state.opciones_actuales):
                    letra_vis = letras[i].upper() if i < len(letras) else str(i+1)
                    with cols[i % 2]:
                        if st.button(f"[{letra_vis}] {op}", use_container_width=True, key=f"btn_op_{idx}_{i}"):
                            procesar_respuesta(op)
            else:
                res = st.session_state.resultado_ronda
                if res["es_correcto"]:
                    st.success(f"✅ ¡Correcto! Acertaste en {res['tiempo']}.")
                else:
                    st.error(f"❌ {res['humano']}")
                
                st.info(f"🤖 **IA:** {res['ia']} | ⏱️ **Tiempo final:** {res['tiempo']}")
                
                if nivel_actual == "DIFICIL":
                    ruta_clara = ruta_img.replace("_borrosa", "_clara")
                    if os.path.exists(ruta_clara):
                        img_clara_b64 = obtener_base64_imagen(ruta_clara)
                        if img_clara_b64:
                            st.markdown(
                                f"""
                                <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 300px; background-color: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; margin: 10px 0;">
                                    <img src="data:image/jpg;base64,{img_clara_b64}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                
                if st.button("Siguiente Imagen ➡️", use_container_width=True, type="primary"):
                    st.session_state.indice_imagen += 1
                    st.session_state.marca_tiempo_inicio = time.time()
                    st.session_state.respondido = False
                    st.rerun()
        else:
            nombre_sin_ext, _ = os.path.splitext(nombre_archivo)
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
                    "Imagen": nombre_archivo.replace("_borrosa", "").replace("_clara", ""),
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
