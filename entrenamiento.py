import streamlit as st
import time
import os
import html
import re

# Función para limpiar nombres de GIFs y ejercicios
def clean_name(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9_]', '_', text)  # reemplaza cualquier caracter raro por _
    return text

# Ejercicios
planes = {
    "Día A – Pierna + Core": [
        {"n": "Sentadillas", "t": 40, "d": "Baja hasta 90º"},
        {"n": "Zancadas", "t": 20, "d": "20'' por pierna", "por_pierna": True},
        {"n": "Puente de glúteo", "t": 35, "d": "Eleva cadera"},
        {"n": "Elevaciones gemelos", "t": 35, "d": "Sube talones lento"},
        {"n": "Plancha frontal", "t": 40, "d": "Espalda recta"},
        {"n": "Plancha lateral der.", "t": 30, "d": "Antebrazo derecho"},
        {"n": "Plancha lateral izq.", "t": 30, "d": "Antebrazo izquierdo"},
    ],
    "Día B – Potencia + Core dinámico": [
        {"n": "Sentadillas salto", "t": 30, "d": "Explosivas"},
        {"n": "Skipping", "t": 20, "d": "Rodillas altas"},
        {"n": "Zancada atrás der.", "t": 20, "d": "Paso atrás der."},
        {"n": "Zancada atrás izq.", "t": 20, "d": "Paso atrás izq."},
        {"n": "Escaladores", "t": 30, "d": "Rápidos"},
        {"n": "Superman", "t": 30, "d": "Eleva brazos y piernas"},
        {"n": "Plancha con toque hombro", "t": 30, "d": "Alterna hombros"},
    ],
}

# Inicializar estado
if "running" not in st.session_state:
    st.session_state.running = False
    st.session_state.idx = 0
    st.session_state.remaining = 0
    st.session_state.exercise = None
    st.session_state.resting = False
    st.session_state.side = 1
    st.session_state.paused = False

# Configuración de página
st.set_page_config(page_title="Entrenador Profesional", layout="wide")
st.title("🏋️ Entrenador de Fuerza - Dashboard Profesional")

# Panel lateral
with st.sidebar:
    st.header("Configuración y progreso")
    plan = st.selectbox("Elige tu rutina", list(planes.keys()))
    rounds = st.number_input("Número de rondas", 1, 10, 1)
    rest_time = st.number_input("Tiempo de descanso (s)", 10, 120, 20, step=5)
    st.markdown("---")
    st.write("Ronda actual:", st.session_state.idx + 1 if st.session_state.running else 0, "de", len(planes[plan]))
    st.write("Ejercicio actual:", st.session_state.exercise["n"] if st.session_state.exercise else "—")
    if st.button("▶️ Empezar / Reiniciar"):
        st.session_state.running = True
        st.session_state.idx = 0
        st.session_state.exercise = planes[plan][0]
        st.session_state.remaining = st.session_state.exercise["t"]
        st.session_state.resting = False
        st.session_state.side = 1
        st.session_state.paused = False

# Área principal
if st.session_state.running:
    placeholder_title = st.empty()
    placeholder_desc = st.empty()
    placeholder_clock = st.empty()

    ex = st.session_state.exercise

    # Botón de pausa / resume
    if st.button("⏸️ Pausa / ▶️ Reanudar"):
        st.session_state.paused = not st.session_state.paused

    if st.session_state.resting:
        placeholder_title.markdown('<div style="font-size:32px; color:#FFA500">😮‍💨 Descanso</div>', unsafe_allow_html=True)
        placeholder_desc.markdown(html.escape("Respira y prepárate"), unsafe_allow_html=True)
        color = "#FFA500"

        # GIF de descanso
        descanso_gif = "descanso.gif"
        if os.path.exists(descanso_gif):
            st.image(descanso_gif, width=300)

        # Botones para +30s y saltar descanso
        col1, col2 = st.columns(2)
        with col1:
            if st.button("+30s de descanso"):
                st.session_state.remaining += 30
        with col2:
            if st.button("Saltar descanso"):
                st.session_state.resting = False
                st.session_state.idx += 1
                if st.session_state.idx < len(planes[plan]):
                    st.session_state.exercise = planes[plan][st.session_state.idx]
                    st.session_state.remaining = st.session_state.exercise["t"]
                    st.session_state.side = 1
                else:
                    st.success("✅ Rutina completada")
                st.rerun()
    else:
        # Nombre y descripción del ejercicio
        name = ex["n"]
        if ex.get("por_pierna"):
            name += f" - Pierna {st.session_state.side}"
        placeholder_title.markdown(f'<div style="font-size:32px; color:#1E90FF">{html.escape(name)}</div>', unsafe_allow_html=True)
        placeholder_desc.markdown(f'<div style="font-size:20px">{html.escape(ex["d"])}</div>', unsafe_allow_html=True)
        color = "#1E90FF"

        # GIF del ejercicio
        gif_name = f"{clean_name(ex['n'])}.gif"
        if os.path.exists(gif_name):
            st.image(gif_name, width=300)

        # Saltar ejercicio
        if st.button("Saltar ejercicio"):
            st.session_state.resting = True
            st.session_state.remaining = rest_time
            st.rerun()

    # Temporizador
    while st.session_state.remaining > 0:
        if not st.session_state.paused:
            mins, secs = divmod(st.session_state.remaining, 60)
            placeholder_clock.markdown(f'<div style="font-size:48px; color:{color}">⏱ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
            time.sleep(1)
            st.session_state.remaining -= 1
        else:
            placeholder_clock.markdown(f'<div style="font-size:48px; color:gray">⏸️ Pausado</div>', unsafe_allow_html=True)
            time.sleep(1)

    # Manejo de pierna
    if not st.session_state.resting:
        if ex.get("por_pierna") and st.session_state.side == 1:
            st.session_state.side = 2
            st.session_state.remaining = ex["t"]
            st.rerun()
        else:
            st.session_state.side = 1
            st.session_state.resting = True
            st.session_state.remaining = rest_time
            st.rerun()
    else:
        st.session_state.resting = False
        st.session_state.idx += 1
        if st.session_state.idx < len(planes[plan]):
            st.session_state.exercise = planes[plan][st.session_state.idx]
            st.session_state.remaining = st.session_state.exercise["t"]
            st.rerun()
        else:
            st.success("✅ Rutina completada")
