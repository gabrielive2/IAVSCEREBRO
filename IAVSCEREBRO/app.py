import streamlit as st
import random
import time
import os

st.set_page_config(page_title="Humano vs IA - Multimodo", layout="centered")
st.title("👤 Humano vs 🤖 IA")

# TU LISTA REAL DE ANIMALES OFICIAL
RESPUESTAS_CORRECTAS = {
    "a1": "Narval", "a2": "Armadillo", "a3": "pez borrón", "a4": "gato",
    "a6": "Tarsero", "a7": "Aye-aye", "a8": "Chimpancé", "a9": "Serpiente",
    "b1": "Delfines", "b2": "Tigre", "b3": "Cucaracha", "b4": "Koala",
    "b5": "Picozapato", "b6": "Capibara", "b7": "Rinoceronte", "b8": "Antilope saiga",
    "b9": "Cebra", "c1": "Caballo de mar", "c2": "Tortuga", "c3": "Murcielago de la fruta con nariz tubular",
    "c4": "Pavo real común", "c5": "gallo", "c6": "Gaur", "c7": "Puma",
    "c8": "Halcón peregrino", "c9": "Iguana azul", "d1": "Panda rojo", "d2": "Oso pardo",
    "d3": "Conejo", "d4": "Oveja", "d5": "Herrerillo común", "d6": "Tucan",
    "d7": "león", "d8": "doberman", "d9": "Pez volador", "e1": "Huemul",
    "e2": "Chinchilla", "e3": "ajolote", "e4": "pez murciélago", "e5": "condor"
}

RUTA_IMAGENES = "imagenes"

if "juego_iniciado" not in st.session_state:
    st.session_state.juego_iniciado = False
    st.session_state.ronda_actual = 0
    st.session_state.fotos_partida = []
    st.session_state.puntos_humano = 0
    st.session_state.tiempo_humano = 0.0
    st.session_state.puntos_ia = 0
    st.session_state.tiempo_ia = 0.0
    st.session_state.ia_procesada = False
    st.session_state.modo_juego = "Escribir nombre"

# PANTALLA DE INICIO (Configuración de la partida)
if not st.session_state.juego_iniciado:
    st.write("### 🎮 Configura tu partida")
    st.write(f"Tenemos un total de {len(RESPUESTAS_CORRECTAS)} imágenes en el sistema. Responderás **10 al azar**.")
   
    # Menú desplegable para elegir el modo de juego
    st.session_state.modo_juego = st.selectbox(
        "Selecciona el modo de juego:",
        ["Escribir nombre (Jugador solo)", "Modo Árbitro (Teclas instantáneas V/X)"]
    )
   
    if st.session_state.modo_juego == "Escribir nombre (Jugador solo)":
        st.info("✍️ **Modo Escribir:** Verás la foto y tendrás que escribir el nombre exacto del animal. Presiona 'Enviar' o la tecla Enter para confirmar.")
    else:
        st.info("🔊 **Modo Árbitro:** El jugador dice el animal por voz. Tú (el réferi) presionas [V] si acierta o [X] si falla. ¡Cambia de foto al instante!")

    if st.button("🚀 Empezar Partida"):
        todas_las_llaves = list(RESPUESTAS_CORRECTAS.keys())
        st.session_state.fotos_partida = random.sample(todas_las_llaves, 10)
        st.session_state.juego_iniciado = True
        st.session_state.ronda_actual = 0
        st.session_state.puntos_humano = 0
        st.session_state.tiempo_humano = 0.0
        st.session_state.puntos_ia = 0
        st.session_state.tiempo_ia = 0.0
        st.session_state.ia_procesada = False
        st.session_state.inicio_cronometro = time.time()
        st.rerun()

# PANTALLA DE JUEGO (10 Rondas)
elif st.session_state.ronda_actual < 10:
    codigo_foto = st.session_state.fotos_partida[st.session_state.ronda_actual]
    respuesta_valida = RESPUESTAS_CORRECTAS[codigo_foto]
   
    st.write(f"### 👤 Foto {st.session_state.ronda_actual + 1} de 10")
   
    # Si es modo árbitro, le mostramos el "chivato" al réferi de qué animal es
    if st.session_state.modo_juego != "Escribir nombre (Jugador solo)":
        st.caption(f"💡 El animal actual es: **{respuesta_valida}**")
   
    # Buscador de imágenes
    ruta_final_imagen = ""
    if os.path.exists(RUTA_IMAGENES):
        archivos_en_carpeta = os.listdir(RUTA_IMAGENES)
        for archivo in archivos_en_carpeta:
            nombre_sin_ext, _ = os.path.splitext(archivo)
            if nombre_sin_ext.lower().strip() == codigo_foto.lower().strip():
                ruta_final_imagen = os.path.join(RUTA_IMAGENES, archivo)
                break
           
    if ruta_final_imagen and os.path.exists(ruta_final_imagen):
        st.image(ruta_final_imagen, use_container_width=True)
    else:
        st.error(f"No se encontró la foto para el código '{codigo_foto}'.")

    # --- LÓGICA SEGÚN EL MODO SELECCIONADO ---
    if st.session_state.modo_juego == "Escribir nombre (Jugador solo)":
        # MODO ESCRIBIR TRADICIONAL
        respuesta_humano = st.text_input("¿Qué animal es este?", key=f"escribir_{st.session_state.ronda_actual}")
       
        if st.button("Enviar Respuesta 📤"):
            tiempo_ronda_humano = time.time() - st.session_state.inicio_cronometro
            st.session_state.tiempo_humano += tiempo_ronda_humano
           
            if respuesta_humano.lower().strip() == respuesta_valida.lower().strip():
                st.session_state.puntos_humano += 1
                st.toast("¡Acertaste! 🎉")
            else:
                st.toast(f"Fallaste ❌ (Era: {respuesta_valida})")
               
            st.session_state.ronda_actual += 1
            st.session_state.inicio_cronometro = time.time()
            st.rerun()
           
    else:
        # MODO ÁRBITRO INSTANTÁNEO CON AUTO-ENFOQUE
        st.info("🎯 Escuchando teclado... Presiona [V] para acierto o [X] para fallo.")
        tecla_pulsada = st.text_input("Receptor", key=f"reflejo_{st.session_state.ronda_actual}", label_visibility="collapsed")

        # Inyección de código oculto para mantener enfocada la caja de texto en Modo Árbitro
        st.components.v1.html(
            f"""
            <script>
                var inputs = window.parent.document.querySelectorAll('input[type="text"]');
                if (inputs.length > 0) {{
                    inputs[inputs.length - 1].focus();
                }}
            </script>
            """,
            height=0,
        )

        if tecla_pulsada:
            letra = tecla_pulsada.lower().strip()
            if letra in ['v', 'x']:
                tiempo_ronda_humano = time.time() - st.session_state.inicio_cronometro
                st.session_state.tiempo_humano += tiempo_ronda_humano
               
                if letra == 'v':
                    st.session_state.puntos_humano += 1
                    st.toast("¡Punto Humano! 🎉")
                else:
                    st.toast("Fallo del Humano ❌")
                   
                st.session_state.ronda_actual += 1
                st.session_state.inicio_cronometro = time.time()
                st.rerun()
            else:
                st.rerun()

# PANTALLA FINAL
else:
    if not st.session_state.ia_processed:
        with st.spinner("🤖 La IA está resolviendo las 10 imágenes..."):
            time.sleep(2.0)
            for foto in st.session_state.fotos_partida:
                st.session_state.tiempo_ia += random.uniform(1.1, 3.8)
                if random.random() < 0.78:
                    st.session_state.puntos_ia += 1
            st.session_state.ia_procesada = True
            st.rerun()

    st.success("🏆 ¡Partida Completada!")
    promedio_humano = round(st.session_state.tiempo_humano / 10, 2)
    promedio_ia = round(st.session_state.tiempo_ia / 10, 2)
   
    ganador_puntos = "👤 Humano" if st.session_state.puntos_humano > st.session_state.puntos_ia else "🤖 IA" if st.session_state.puntos_ia > st.session_state.puntos_humano else "Empate 🤝"
    ganador_tiempo = "👤 Humano" if st.session_state.tiempo_humano < st.session_state.tiempo_ia else "🤖 IA"
    ganador_promedio = "👤 Humano" if promedio_humano < promedio_ia else "🤖 IA"

    tabla_resultados = {
        "Métrica": ["Aciertos Totales", "Tiempo Total", "Tiempo Promedio por Foto"],
        "👤 Humano": [f"{st.session_state.puntos_humano} / 10", f"{round(st.session_state.tiempo_humano, 2)} s", f"{promedio_humano} s"],
        "🤖 IA (Bot)": [f"{st.session_state.puntos_ia} / 10", f"{round(st.session_state.tiempo_ia, 2)} s", f"{promedio_ia} s"],
        "🏆 Ganador": [ganador_puntos, ganador_tiempo, ganador_promedio]
    }
    st.table(tabla_resultados)
    if st.button("🔄 Jugar Nueva Partida"):
        st.session_state.juego_iniciado = False
        st.rerun()

