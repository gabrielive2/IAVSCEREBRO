import streamlit as st
import os
import time
import random

# Configuración inicial de la página
st.set_page_config(page_title="IAVSCEREBRO - Quiz", layout="centered")

# =====================================================================
# 1. CONFIGURACIÓN DE RUTAS Y CONSTANTES
# =====================================================================
FONDO_PATH = "fondo/naturaleza.jpg"
CARPETA_FACIL = "faciles"
CARPETA_INTERMEDIA = "intermedias"
CARPETA_DIFICIL = "dificiles" # Dejado listo para cuando añadas tus 20 imágenes

IMAGENES_POR_BLOQUE = 5

# =====================================================================
# 2. INICIALIZACIÓN DEL ESTADO DE SESIÓN (SESSION STATE)
# =====================================================================
if "fase" not in st.session_state:
    # Fases del flujo: INICIO -> PANTALLA_FACIL -> QUIZ_FACIL -> PANTALLA_INTERMEDIA -> QUIZ_INTERMEDIA -> PANTALLA_DIFICIL -> QUIZ_DIFICIL -> FINAL
    st.session_state.fase = "INICIO"
    st.session_state.imagenes_partida = []
    st.session_state.indice_imagen = 0
    st.session_state.resultados = [] # Lista de diccionarios para recopilar la información final
    st.session_state.marca_tiempo_inicio = 0.0

# Función interna para cargar 5 imágenes aleatorias .jpg de una carpeta
def obtener_muestra_imagenes(carpeta):
    if os.path.exists(carpeta):
        archivos = [
            os.path.join(carpeta, f) 
            for f in os.listdir(carpeta) 
            if f.lower().endswith('.jpg')
        ]
        if len(archivos) >= IMAGENES_POR_BLOQUE:
            return random.sample(archivos, IMAGENES_POR_BLOQUE)
        return archivos
    return []

# =====================================================================
# 3. INTERFAZ DE USUARIO Y FLUJO DEL QUIZ
# =====================================================================

# --- PANTALLA DE INICIO ---
if st.session_state.fase == "INICIO":
    st.title("🧠 BIENVENIDO A IAVSCEREBRO")
    
    # Renderizar imagen de inicio
    if os.path.exists(FONDO_PATH):
        st.image(FONDO_PATH, use_container_width=True)
    else:
        st.warning(f"Por favor, añade la imagen en la ruta: '{FONDO_PATH}'")
        
    if st.button("🚀 Comenzar Evaluación", type="primary", use_container_width=True):
        st.session_state.fase = "PANTALLA_FACIL"
        st.rerun()

# --- PANTALLA INTERMEDIA: FÁCIL ---
elif st.session_state.fase == "PANTALLA_FACIL":
    st.subheader("🟢 Nivel Inicial")
    st.title("IMÁGENES FÁCILES")
    st.write("Presiona el botón para comenzar. Responde usando tu teclado de forma instantánea.")
    
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
    st.write("Preparado para el siguiente bloque. Los controles siguen siendo los mismos.")
    
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
    st.write("Bloque final del quiz IAVSCEREBRO.")
    
    # Comprobar si la carpeta tiene imágenes cargadas
    imagenes_dificiles = obtener_muestra_imagenes(CARPETA_DIFICIL)
    
    if not imagenes_dificiles:
        st.info("ℹ️ Bloque difícil vacío por el momento. Avanzando automáticamente a los resultados finales.")
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
    # Extraer el nombre legible de la dificultad
    nivel_actual = st.session_state.fase.replace("QUIZ_", "")
    lista_actual = st.session_state.imagenes_partida
    idx = st.session_state.indice_imagen

    if idx < len(lista_actual):
        ruta_img = lista_actual[idx]
        nombre_archivo = os.path.basename(ruta_img)
        
        st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")
        st.image(ruta_img, use_container_width=True)
        
        # --- Cronómetro en milisegundos en tiempo real ---
        tiempo_actual = time.time()
        milisegundos_transcurridos = int((tiempo_actual - st.session_state.marca_tiempo_inicio) * 1000)
        
        st.markdown(f"⏱️ **Tiempo transcurrido:** `{milisegundos_transcurridos} ms`")
        
        # Input camuflado para capturar las teclas de manera inmediata
        st.write("👇 Presiona **V** (Acertó) o **X** (Falló) en tu teclado:")
        entrada_teclado = st.text_input(
            "Captura", 
            key=f"tecla_{st.session_state.fase}_{idx}", 
            label_visibility="collapsed"
        )

        # Inyección JavaScript para forzar el enfoque inmediato en el campo de texto
        st.components.v1.html(
            """
            <script>
                var inputs = window.parent.document.querySelectorAll('input[type="text"]');
                if (inputs.length > 0) {
                    inputs[inputs.length - 1].focus();
                }
            </script>
            """,
            height=0,
        )

        # Evaluar la tecla presionada de inmediato
        if entrada_teclado:
            accion = entrada_teclado.lower().strip()
            if accion in ['v', 'x']:
                # Registrar dict de datos finales
                resultado_concursante = "Acertó" if accion == 'v' else "Falló"
                
                # Simulación de respuesta paralela de la IA basada en el tiempo real
                tiempo_ia_ms = int(milisegundos_transcurridos * random.uniform(0.6, 0.9))
                
                st.session_state.resultados.append({
                    "Imagen / Estructura": nombre_archivo,
                    "Nivel de Dificultad": nivel_actual,
                    "Tiempo Humano (ms)": milisegundos_transcurridos,
                    "Estado Concursante": resultado_concursante,
                    "Tiempo IA (ms)": tiempo_ia_ms
                })
                
                # Forzar el salto directo a la siguiente imagen
                st.session_state.indice_imagen += 1
                st.session_state.marca_tiempo_inicio = time.time()
                st.rerun()
            else:
                # Si presionan cualquier otra tecla, limpia el input y mantiene la espera
                st.rerun()
                
        # Auto-refresco controlado para actualizar visualmente los milisegundos del cronómetro
        time.sleep(0.05)
        st.rerun()
        
    else:
        # Control de transiciones al agotar las 5 imágenes del bloque actual
        if st.session_state.fase == "QUIZ_FACIL":
            st.session_state.fase = "PANTALLA_INTERMEDIA"
        elif st.session_state.fase == "QUIZ_INTERMEDIA":
            st.session_state.fase = "PANTALLA_DIFICIL"
        elif st.session_state.fase == "QUIZ_DIFICIL":
            st.session_state.fase = "FINAL"
        st.rerun()

# --- TABLA FINAL DE METRICAS ---
elif st.session_state.fase == "FINAL":
    st.title("📊 MÉTRICAS FINALES — IAVSCEREBRO")
    st.success("¡Prueba concluida exitosamente!")
    
    st.write("### Tabla Comparativa de Tiempos de la IA vs Humano")
    if st.session_state.resultados:
        # Generar tabla limpia nativa en base a la lista recolectada
        st.table(st.session_state.resultados)
    else:
        st.info("No se recolectaron datos durante el quiz.")
        
    if st.button("🔄 Reiniciar Nueva Evaluación", use_container_width=True):
        st.session_state.clear()
        st.rerun()


