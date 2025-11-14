import streamlit as st
import random

COLORS = {"U": "white", "D": "yellow", "F": "green", "B": "blue", "L": "orange", "R": "red"}
COLOR_HEX = {"white":"#FFFFFF", "yellow":"#ffec00", "green":"#1eab39", "blue":"#0854aa", "orange":"#ff9900", "red":"#e6000a"}

MOVES = ["R", "Ri", "L", "Li", "U", "Ui", "D", "Di", "F", "Fi", "B", "Bi"]
EXPLAIN = {
    "R": "Gira la cara derecha en sentido horario",
    "Ri": "Gira la cara derecha en sentido antihorario",
    "L": "Gira la cara izquierda en sentido horario",
    "Li": "Gira la cara izquierda en sentido antihorario"
    # Puedes agregar más explicaciones para otros movimientos
}

def cubo_resuelto():
    return {c: [COLORS[c]]*9 for c in COLORS}

def aplicar_movimiento(cube, movimiento):
    # Solo definimos unos movimientos para demo
    if movimiento == "R":
        old = cube["R"][:]
        cube["R"] = [old[6],old[3],old[0],old[7],old[4],old[1],old[8],old[5],old[2]]
    if movimiento == "Ri":
        for _ in range(3): cube = aplicar_movimiento(cube, "R")
    if movimiento == "L":
        old = cube["L"][:]
        cube["L"] = [old[6],old[3],old[0],old[7],old[4],old[1],old[8],old[5],old[2]]
    if movimiento == "Li":
        for _ in range(3): cube = aplicar_movimiento(cube, "L")
    # Puedes agregar D, U, F, B si quieres más realismo
    return cube

def mezclar_cubo(n=8):
    cube = cubo_resuelto()
    mezcla = random.choices(list(EXPLAIN.keys()), k=n)
    for mov in mezcla:
        cube = aplicar_movimiento(cube, mov)
    return cube, mezcla

def draw_face(face, name):
    html = f"<b>{name}</b><br><table style='border-collapse:collapse;border:2px solid black;'>"
    for i in range(3):
        html += "<tr>"
        for j in range(3):
            color = COLOR_HEX[face[3*i+j]]
            html += f"<td style='background:{color};width:27px;height:27px;border:1px solid #444'></td>"
        html += "</tr>"
    html += "</table>"
    return html

def draw_cube(cube):
    for x in ["U", "F", "R", "L", "D", "B"]:
        st.markdown(draw_face(cube[x], x), unsafe_allow_html=True)

st.title("Rubik 3x3 Interactivo - Aleatorio y Solución Manual")

if "cube" not in st.session_state:
    cube, scramble = mezclar_cubo(8)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0

if st.button("Nuevo cubo aleatorio"):
    cube, scramble = mezclar_cubo(8)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0

st.markdown("### Estado actual del cubo (las 6 caras)")
draw_cube(st.session_state.cube)
st.markdown(f"**Mezcla aplicada:** {' → '.join(st.session_state.scramble)}")
st.markdown(f"**Secuencia para resolver:** {' → '.join(st.session_state.solve_seq)}")
if st.session_state.step < len(st.session_state.solve_seq):
    next_move = st.session_state.solve_seq[st.session_state.step]
    st.info(f"Siguiente: {EXPLAIN[next_move]}")
    if st.button("Aplicar siguiente movimiento para resolver"):
        st.session_state.cube = aplicar_movimiento(st.session_state.cube, next_move)
        st.session_state.step += 1
else:
    st.success("¡Cubo resuelto! Puedes mezclar de nuevo o probar otro reto.")

st.caption("Este flujo es totalmente soportado en Streamlit Cloud: no usa dependencias externas ni compilación especial.")
