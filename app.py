import streamlit as st
import random
from rubik_solver import utils

# Diccionario para mapeo visual (¡no cambiar!)
color_hex = {"W":"#fff", "Y":"#ffec00", "G":"#1eab39", "B":"#0854aa", "O":"#ff9900", "R":"#e6000a"}
order = ['U', 'R', 'F', 'D', 'L', 'B']  # Kociemba/rubik_solver face order

def random_cube_state():
    # Crea la string del cubo mezclado usando rubik_solver (mejora sobre aleatorio puro)
    scramble = utils.gen_scramble()
    cube_str = utils.apply_scramble(utils.solve("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB", "Beginner"), scramble)
    return cube_str, scramble

def draw_cube(cube_str):
    faces = {face: list(cube_str[i*9:(i+1)*9]) for i, face in enumerate(order)}
    face_names = {'U':'Arriba (U)', 'R':'Derecha (R)', 'F':'Frente (F)', 'D':'Abajo (D)', 'L':'Izquierda (L)', 'B':'Atrás (B)'}
    for face in order:
        st.markdown(f"**{face_names[face]}**")
        html = "<table style='border-collapse:collapse;border:2px solid #222;'>"
        for i in range(3):
            html += "<tr>"
            for j in range(3):
                color = color_hex[faces[face][i*3+j]]
                html += f"<td style='background:{color};width:36px;height:36px;border:1px solid #444'></td>"
            html += "</tr>"
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)

st.title("Rubik's Cube - Aleatorio y Solución Óptima")

# Estado inicial: cubo aleatorio válido y scramble
if "cube_str" not in st.session_state:
    cube_str, scramble = random_cube_state()
    st.session_state.cube_str = cube_str
    st.session_state.scramble = scramble

if st.button("Nuevo cubo aleatorio"):
    cube_str, scramble = random_cube_state()
    st.session_state.cube_str = cube_str
    st.session_state.scramble = scramble

st.markdown("### Estado del cubo mezclado")
draw_cube(st.session_state.cube_str)

st.markdown(f"**Secuencia de mezcla aplicada:** {' '.join(st.session_state.scramble)}")

# ---- SOLUCIÓN -----
try:
    solution = utils.solve(st.session_state.cube_str, "Kociemba")
    st.success(f"Secuencia óptima de solución encontrara: {len(solution)} movimientos")
    st.markdown(f"**Movimientos para resolver:** {' '.join(solution)}")
    # Explicación paso a paso
    for idx, move in enumerate(solution, 1):
        st.info(f"Paso {idx}: Realiza el giro {move}")
except Exception as e:
    st.error(f"No se pudo calcular la solución. ¿El cubo es válido? Error: {e}")

st.caption("Powered by rubik_solver (basado en Kociemba). Puedes usar esto como simulador, reto o tutorial.")