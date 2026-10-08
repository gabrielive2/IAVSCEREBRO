import streamlit as st
import streamlit.components.v1 as components
import os
import time
import random
import base64
import unicodedata
import json

st.set_page_config(page_title="IAVSCEREBRO - Quiz", layout="centered")

FONDO_PATH = "fondo/naturaleza.jpg"
CARPETA_FACIL = "faciles"
CARPETA_INTERMEDIA = "intermedias"
CARPETA_DIFICIL = "dificiles"
IMAGENES_POR_BLOQUE = 5
# Enlace al mp3 subido a tu repositorio de GitHub (repo público), a través de jsDelivr.
# Formato: https://cdn.jsdelivr.net/gh/USUARIO/REPOSITORIO@main/musica.mp3
MUSICA_URL = "https://cdn.jsdelivr.net/gh/TU_USUARIO/TU_REPOSITORIO@main/musica.mp3"

# IAs simuladas: probabilidad de acierto por nivel y rango de tiempo de respuesta (segundos).
# Son valores inventados y editables: no se consulta ninguna IA real.
IAS = {
    "Gemini":  {"acierto": {"FACIL": 0.95, "INTERMEDIA": 0.85, "DIFICIL": 0.70}, "tiempo": (0.8, 2.0)},
    "Claude":  {"acierto": {"FACIL": 0.95, "INTERMEDIA": 0.88, "DIFICIL": 0.75}, "tiempo": (1.0, 2.5)},
    "ChatGPT": {"acierto": {"FACIL": 0.96, "INTERMEDIA": 0.86, "DIFICIL": 0.72}, "tiempo": (0.9, 2.2)},
    "Grok":    {"acierto": {"FACIL": 0.92, "INTERMEDIA": 0.80, "DIFICIL": 0.62}, "tiempo": (0.7, 1.8)},
}

MODO_ALTERNATIVAS = "Modo Alternativas (1, 2, 3, 4)"
MODO_ESCRIBIR = "Modo Escribir Nombre"
MODO_ARBITRO = "Modo Árbitro (Espacio, T, F)"

defaults = {
    "fase": "INICIO",
    "modo_juego": MODO_ALTERNATIVAS,
    "imagenes_partida": [],
    "indice_imagen": 0,
    "resultados": [],
    "marca_tiempo_inicio": 0.0,
    "opciones_actuales": [],
    "respuesta_correcta": "",
    "respondido": False,
    "resultado_ronda": {},
    "ultima_idx": -1,
    # Modo Árbitro
    "pausado": False,          # True cuando se presionó Espacio (tiempo detenido)
    "tiempo_pausa_s": 0.0,     # segundos transcurridos al presionar Espacio
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
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
                if f.lower().endswith(('.png', '.jpeg')) and "_borrosa" in f.lower()
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


def normalizar(texto):
    """Minúsculas, sin tildes, sin guiones bajos y sin espacios de más."""
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.replace("_", " ").lower().split())


def nombre_desde_archivo(nombre_archivo):
    base = os.path.splitext(nombre_archivo)[0]
    return base.replace("_borrosa", "").replace("_clara", "").replace("_", " ").title()


def buscar_clara(ruta_borrosa):
    """Devuelve la ruta de la versión _clara de una imagen _borrosa (o None)."""
    carpeta = os.path.dirname(ruta_borrosa)
    base = os.path.splitext(os.path.basename(ruta_borrosa))[0]
    objetivo = base.lower().replace("_borrosa", "_clara")
    if os.path.isdir(carpeta):
        for f in os.listdir(carpeta):
            nombre, ext = os.path.splitext(f)
            if nombre.lower() == objetivo and ext.lower() in (".png", ".jpeg", ".png"):
                return os.path.join(carpeta, f)
    return None


def iniciar_bloque(imagenes, fase_quiz):
    st.session_state.imagenes_partida = imagenes
    st.session_state.indice_imagen = 0
    st.session_state.ultima_idx = -1      # fuerza regenerar opciones en la 1ª imagen
    st.session_state.respondido = False
    st.session_state.pausado = False
    st.session_state.fase = fase_quiz
    st.session_state.marca_tiempo_inicio = time.time()
    st.rerun()


# ----------------------------------------------------------------------
# Cronómetro + atajos de teclado (un solo componente HTML/JS)
# ----------------------------------------------------------------------
# IMPORTANTE: st.markdown NO ejecuta <script>. Para correr JavaScript hay que
# usar components.html, que lo ejecuta dentro de un iframe.
#
# Atajos (el script mira qué botones hay en pantalla, así que sirve para todos los modos):
#   1 / 2 / 3 / 4  -> alternativas (modo Alternativas)
#   Espacio        -> "Parar tiempo" (modo Árbitro) y congela el cronómetro al instante
#   T / F          -> decisión del árbitro: T = acertó, F = falló (después de parar el tiempo)
#   Enter          -> Siguiente imagen
COMPONENTE_HTML = """
<style>
  body { margin: 0; background: transparent; font-family: sans-serif; }
  .crono {
    display: inline-block; background: #1f2937; color: #ffffff;
    padding: 6px 14px; border-radius: 20px; font-size: 18px; font-weight: bold;
  }
</style>
<div class="crono">⏱️ Tiempo transcurrido: <span id="crono">0.0</span> s</div>

<script>
(function () {
  // ---------- Cronómetro ----------
  const detenido = %%DETENIDO%%;
  const transcurrido = %%TRANSCURRIDO%%;   // segundos que ya pasaron (calculado en Python)
  const el = document.getElementById('crono');
  let intervalo = null;

  if (detenido) {
    el.innerText = transcurrido.toFixed(1);
  } else {
    const inicio = Date.now() - transcurrido * 1000;
    const tick = () => { el.innerText = ((Date.now() - inicio) / 1000).toFixed(1); };
    tick();
    intervalo = setInterval(tick, 100);
  }

  // ---------- Atajos de teclado ----------
  const P = window.parent;
  if (P.__iavHandler) {
    P.document.removeEventListener('keydown', P.__iavHandler);
  }
  P.__iavHandler = function (e) {
    const t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA')) return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;

    const botones = Array.from(P.document.querySelectorAll('button'));
    const k = e.key.toLowerCase();
    let destino = null;

    if (e.code === 'Space') {
      destino = botones.find(b => b.innerText.includes('Parar tiempo'));
      if (destino) {
        if (intervalo) clearInterval(intervalo);   // congela el reloj al instante
        if (P.document.activeElement) P.document.activeElement.blur();
      }
    } else if (k.length === 1 && '1234tf'.includes(k)) {
      destino = botones.find(b => b.innerText.trim().toLowerCase().startsWith('[' + k + ']'));
    } else if (k === 'm') {
      // M = silenciar / activar el sonido de la música (sin recargar nada)
      if (P.__iavAudio) P.__iavAudio.muted = !P.__iavAudio.muted;
      return;
    } else if (e.key === 'Enter') {
      destino = botones.find(b => b.innerText.includes('Siguiente'));
    }

    if (destino) {
      e.preventDefault();
      destino.click();
    }
  };
  P.document.addEventListener('keydown', P.__iavHandler);
})();
</script>
"""


def mostrar_cronometro(transcurrido, detenido):
    html = (
        COMPONENTE_HTML
        .replace("%%DETENIDO%%", "true" if detenido else "false")
        .replace("%%TRANSCURRIDO%%", f"{max(0.0, transcurrido):.3f}")
    )
    components.html(html, height=50)


# ----------------------------------------------------------------------
# Música de fondo
# ----------------------------------------------------------------------
# Claves para que la página no se cuelgue:
#  1) El mp3 NO se mete en el código de la página (nada de base64 ni st.audio):
#     se carga desde un enlace externo (GitHub vía jsDelivr) y el navegador lo descarga UNA vez.
#  2) El <audio> se crea una sola vez en la página principal, así que Streamlit puede
#     re-ejecutar el script cientos de veces sin cortar ni reiniciar la música.
#  3) Solo se toca el audio cuando cambia el volumen o el interruptor.
MUSICA_HTML = """
<script>
(function () {
  const P = window.parent;
  const activa = %%ACTIVA%%;
  const volumen = %%VOLUMEN%%;
  const src = %%URL%%;

  if (!P.__iavAudio) {
    const a = P.document.createElement('audio');
    a.src = src;
    a.loop = true;
    a.preload = 'auto';
    P.document.body.appendChild(a);
    P.__iavAudio = a;
  }
  const audio = P.__iavAudio;

  // Los navegadores bloquean el autoplay hasta que hay un clic o una tecla: se arranca ahí.
  ['click', 'keydown', 'touchstart'].forEach(ev => {
    if (P.__iavArrancar) P.document.removeEventListener(ev, P.__iavArrancar);
  });
  P.__iavArrancar = function () {
    if (P.__iavActiva && P.__iavAudio.paused) P.__iavAudio.play().catch(() => {});
  };
  ['click', 'keydown', 'touchstart'].forEach(ev => P.document.addEventListener(ev, P.__iavArrancar));

  // Solo se toca el audio si cambió la configuración
  const cfg = activa + '|' + volumen;
  if (P.__iavCfg !== cfg) {
    P.__iavCfg = cfg;
    P.__iavActiva = activa;
    audio.volume = volumen;
    if (activa) { audio.play().catch(() => {}); } else { audio.pause(); }
  }
})();
</script>
"""


def iniciar_musica():
    with st.expander("🎵 Música"):
        if "TU_USUARIO" in MUSICA_URL:https://cdn.jsdelivr.net/gh/TU_USUARIO/TU_REPOSITORIO@main/musica.mp3
            st.warning("Falta configurar MUSICA_URL al inicio del código con el enlace a tu mp3 en GitHub.")
            return
        activa = st.checkbox("Música de fondo", value=True, key="musica_activa")
        volumen = st.slider("Volumen", 0, 100, 30, key="musica_volumen")
        st.caption("Durante el quiz, la tecla M silencia o activa el sonido.")

    html = (
        MUSICA_HTML
        .replace("%%ACTIVA%%", "true" if activa else "false")
        .replace("%%VOLUMEN%%", f"{volumen / 100:.2f}")
        .replace("%%URL%%", json.dumps(MUSICA_URL))
    )
    components.html(html, height=0)


iniciar_musica()


# ----------------------------------------------------------------------
# Fases
# ----------------------------------------------------------------------
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
        [MODO_ALTERNATIVAS, MODO_ESCRIBIR, MODO_ARBITRO]
    )

    if st.session_state.modo_juego == MODO_ALTERNATIVAS:
        st.info("🎯 **Modo Alternativas:** Presiona las teclas **1, 2, 3 o 4** (o haz clic) para responder. "
                "Con **Enter** pasas a la siguiente imagen.")
    elif st.session_state.modo_juego == MODO_ARBITRO:
        st.info("⚖️ **Modo Árbitro:** El jugador dice en voz alta el nombre del animal y presiona **Espacio** "
                "para detener el tiempo. Entonces el árbitro ve el nombre correcto y decide con **T** "
                "(acertó) o **F** (falló). Con **Enter** se pasa a la siguiente imagen.")
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
        iniciar_bloque(obtener_muestra_imagenes(CARPETA_FACIL), "QUIZ_FACIL")

elif st.session_state.fase == "PANTALLA_INTERMEDIA":
    st.subheader("🟡 Nivel Moderado")
    st.title("IMÁGENES INTERMEDIAS")
    st.write("Subiendo de nivel. Prepárate para el siguiente reto.")
    if st.button("Iniciar Bloque Intermedio", use_container_width=True):
        iniciar_bloque(obtener_muestra_imagenes(CARPETA_INTERMEDIA), "QUIZ_INTERMEDIA")

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
            iniciar_bloque(imagenes_dificiles, "QUIZ_DIFICIL")

elif st.session_state.fase in ["QUIZ_FACIL", "QUIZ_INTERMEDIA", "QUIZ_DIFICIL"]:
    nivel_actual = st.session_state.fase.replace("QUIZ_", "")
    lista_actual = st.session_state.imagenes_partida
    idx = st.session_state.indice_imagen

    if idx < len(lista_actual):
        ruta_img = lista_actual[idx]
        nombre_archivo = os.path.basename(ruta_img)
        nombre_correcto = nombre_desde_archivo(nombre_archivo)

        # Preparar la ronda (una sola vez por imagen)
        if st.session_state.ultima_idx != idx:
            st.session_state.respuesta_correcta = nombre_correcto
            st.session_state.respondido = False
            st.session_state.pausado = False
            st.session_state.tiempo_pausa_s = 0.0
            st.session_state.resultado_ronda = {}
            st.session_state.ultima_idx = idx

            if st.session_state.modo_juego == MODO_ALTERNATIVAS:
                carpeta_map = {"FACIL": CARPETA_FACIL, "INTERMEDIA": CARPETA_INTERMEDIA, "DIFICIL": CARPETA_DIFICIL}
                carpeta_obj = carpeta_map.get(nivel_actual, CARPETA_FACIL)

                nombres_pool = []
                archivos_carpeta = os.listdir(carpeta_obj) if os.path.isdir(carpeta_obj) else []
                for f in archivos_carpeta:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        n = nombre_desde_archivo(f)
                        if n not in nombres_pool:
                            nombres_pool.append(n)

                distractores = [n for n in nombres_pool if normalizar(n) != normalizar(nombre_correcto)]
                random.shuffle(distractores)
                opciones = distractores[:3] + [nombre_correcto]
                random.shuffle(opciones)
                st.session_state.opciones_actuales = opciones

        st.write(f"### Nivel {nivel_actual} — Imagen {idx + 1} de {len(lista_actual)}")

        ruta_mostrar = ruta_img
        if nivel_actual == "DIFICIL" and st.session_state.respondido:
            ruta_clara = buscar_clara(ruta_img)
            if ruta_clara:
                ruta_mostrar = ruta_clara
            else:
                st.warning("No se encontró la versión _clara de esta imagen.")

        if os.path.exists(ruta_mostrar):
            img_b64_data = obtener_base64_imagen(ruta_mostrar)
            if img_b64_data:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; width: 100%; height: 380px; background-color: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; margin-bottom: 15px;">
                        <img src="data:image/jpeg;base64,{img_b64_data}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.error(f"No se pudo cargar la imagen en la ruta: {ruta_img}")

        # Cronómetro: corre mientras no se responde (ni se pausa); si se presionó Espacio
        # o ya se respondió, queda congelado
        if st.session_state.respondido:
            mostrar_cronometro(st.session_state.resultado_ronda["tiempo_s"], detenido=True)
        elif st.session_state.pausado:
            mostrar_cronometro(st.session_state.tiempo_pausa_s, detenido=True)
        else:
            transcurrido = time.time() - st.session_state.marca_tiempo_inicio
            mostrar_cronometro(transcurrido, detenido=False)

        letras = ["1", "2", "3", "4"]

        def procesar_respuesta(respuesta, segundos=None, arbitro_acerto=None):
            """arbitro_acerto: None en los modos normales; True/False cuando decide el árbitro."""
            if segundos is None:
                segundos = round(time.time() - st.session_state.marca_tiempo_inicio, 1)
            correcta = st.session_state.respuesta_correcta

            if arbitro_acerto is None:
                es_correcto = normalizar(respuesta) == normalizar(correcta)
            else:
                es_correcto = arbitro_acerto
            resultado_humano = "Acertó" if es_correcto else f"Falló (Era: {correcta})"

            fila = {
                "Imagen": nombre_archivo.replace("_borrosa", "").replace("_clara", ""),
                "Nivel": nivel_actual,
                "Tiempo Humano": f"{segundos} s",
                "Humano": resultado_humano,
            }
            ias_ronda = []
            for nombre_ia, cfg in IAS.items():
                acerto = random.random() < cfg["acierto"][nivel_actual]
                t_ia = round(random.uniform(*cfg["tiempo"]), 1)
                texto = "Acertó" if acerto else "Falló"
                fila[nombre_ia] = texto
                fila[f"Tiempo {nombre_ia}"] = f"{t_ia} s"
                ias_ronda.append({"IA": nombre_ia, "Resultado": texto, "Tiempo": f"{t_ia} s"})

            st.session_state.resultados.append(fila)

            st.session_state.respondido = True
            st.session_state.resultado_ronda = {
                "es_correcto": es_correcto,
                "humano": resultado_humano,
                "ias": ias_ronda,
                "tiempo": f"{segundos} s",
                "tiempo_s": segundos,
                "arbitro_acerto": arbitro_acerto,
            }
            st.rerun()

        if not st.session_state.respondido:
            if st.session_state.modo_juego == MODO_ALTERNATIVAS:
                st.write("🎯 **Selecciona la alternativa correcta** (teclas 1, 2, 3, 4):")
                cols = st.columns(2)
                for i, op in enumerate(st.session_state.opciones_actuales):
                    letra_vis = letras[i] if i < len(letras) else str(i + 1)
                    with cols[i % 2]:
                        if st.button(f"[{letra_vis}] {op}", use_container_width=True, key=f"btn_op_{idx}_{i}"):
                            procesar_respuesta(op)

            elif st.session_state.modo_juego == MODO_ARBITRO:
                if not st.session_state.pausado:
                    st.write("🗣️ El jugador dice el nombre del animal y presiona **Espacio** para detener el tiempo.")
                    if st.button("⏸️ Parar tiempo (Espacio)", use_container_width=True, key=f"btn_pausa_{idx}"):
                        st.session_state.tiempo_pausa_s = round(time.time() - st.session_state.marca_tiempo_inicio, 1)
                        st.session_state.pausado = True
                        st.rerun()
                else:
                    # El nombre correcto solo se muestra al árbitro una vez detenido el tiempo
                    st.markdown(f"### ⚖️ Árbitro: el animal es **{st.session_state.respuesta_correcta}**")
                    st.write("⏸️ **Tiempo detenido.** ¿Acertó el jugador? **T** = sí, **F** = no:")
                    col_v, col_f = st.columns(2)
                    with col_v:
                        if st.button("[T] Verdadero (acertó)", use_container_width=True, key=f"btn_t_{idx}"):
                            procesar_respuesta(
                                "",
                                segundos=st.session_state.tiempo_pausa_s,
                                arbitro_acerto=True,
                            )
                    with col_f:
                        if st.button("[F] Falso (falló)", use_container_width=True, key=f"btn_f_{idx}"):
                            procesar_respuesta(
                                "",
                                segundos=st.session_state.tiempo_pausa_s,
                                arbitro_acerto=False,
                            )

            else:
                with st.form(key=f"form_{st.session_state.fase}_{idx}"):
                    respuesta_escrita = st.text_input("¿Qué animal es este? (Escribe el nombre y presiona Enter):")
                    enviado = st.form_submit_button("Responder")
                if enviado and respuesta_escrita.strip():
                    procesar_respuesta(respuesta_escrita)
        else:
            res = st.session_state.resultado_ronda
            if res["es_correcto"]:
                st.success(f"✅ ¡Correcto! Acertaste en {res['tiempo']}.")
            else:
                st.error(f"❌ {res['humano']}")

            if res.get("arbitro_acerto") is not None:
                decision = "T (acertó)" if res["arbitro_acerto"] else "F (falló)"
                st.write(f"⚖️ Decisión del árbitro: **{decision}**. El animal era **{st.session_state.respuesta_correcta}**.")

            st.info(f"⏱️ **Tu tiempo final:** {res['tiempo']}")
            st.write("🤖 **Así les fue a las IAs:**")
            st.table(res["ias"])

            if st.button("Siguiente Imagen ➡️ (Enter)", use_container_width=True, type="primary"):
                st.session_state.indice_imagen += 1
                st.session_state.marca_tiempo_inicio = time.time()
                st.session_state.respondido = False
                st.session_state.pausado = False
                st.rerun()
    else:
        if st.session_state.fase == "QUIZ_FACIL":
            st.session_state.fase = "PANTALLA_INTERMEDIA"
        elif st.session_state.fase == "QUIZ_INTERMEDIA":
            st.session_state.fase = "PANTALLA_DIFICIL"
        elif st.session_state.fase == "QUIZ_DIFICIL":
            st.session_state.fase = "FINAL"
        st.session_state.indice_imagen = 0
        st.session_state.ultima_idx = -1
        st.session_state.respondido = False
        st.session_state.pausado = False
        st.session_state.marca_tiempo_inicio = time.time()
        st.rerun()

elif st.session_state.fase == "FINAL":
    st.title("📊 MÉTRICAS FINALES — IAVSCEREBRO")
    st.success("¡Prueba concluida exitosamente!")
    if st.session_state.resultados:
        st.write("### 🏆 Marcador")
        participantes = ["Humano"] + list(IAS.keys())
        marcador = []
        for nombre in participantes:
            aciertos = 0
            tiempos = []
            for fila in st.session_state.resultados:
                if str(fila[nombre]).startswith("Acertó"):
                    aciertos += 1
                clave_t = "Tiempo Humano" if nombre == "Humano" else f"Tiempo {nombre}"
                tiempos.append(float(fila[clave_t].replace(" s", "")))
            marcador.append({
                "Participante": "🧠 Humano" if nombre == "Humano" else f"🤖 {nombre}",
                "Aciertos": f"{aciertos} / {len(st.session_state.resultados)}",
                "Tiempo promedio": f"{round(sum(tiempos) / len(tiempos), 1)} s",
                "_orden": aciertos,
            })
        marcador.sort(key=lambda m: -m["_orden"])
        for m in marcador:
            m.pop("_orden")
        st.table(marcador)

    st.write("### Tabla Comparativa Completa")
    if st.session_state.resultados:
        st.dataframe(st.session_state.resultados, use_container_width=True)
    else:
        st.info("No hay datos registrados en esta partida.")
