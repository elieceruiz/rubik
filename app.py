import streamlit as st
import random
import copy

# Nombres de las caras
FACE_NAMES = ["Arriba", "Frontal", "Derecha", "Izquierda", "Abajo", "Atrás"]
COLOR_MAP = {
    "Arriba": "white", "Frontal": "green", "Derecha": "red",
    "Izquierda": "orange", "Abajo": "yellow", "Atrás": "blue"
}
COLOR_HEX = {
    "white":"#FFFFFF", "yellow":"#ffec00", "green":"#1eab39",
    "blue":"#0854aa", "orange":"#ff9900", "red":"#e6000a"
}

# Movimientos disponibles (solo unos ejemplos didácticos)
MOVES = [
    ("Arriba", "derecha"), ("Arriba", "izquierda"),
    ("Frontal", "derecha"), ("Frontal", "izquierda"),
    ("Derecha", "abajo"), ("Derecha", "arriba")
]

INSTRUCTIONS = {
    ("Arriba", "derecha"): "Gira la cara de arriba hacia la derecha.",
    ("Arriba", "izquierda"): "Gira la cara de arriba hacia la izquierda.",
    ("Frontal", "derecha"): "Gira la cara frontal hacia la derecha.",
    ("Frontal", "izquierda"): "Gira la cara frontal hacia la izquierda.",
    ("Derecha", "abajo"): "Gira la cara derecha hacia abajo.",
    ("Derecha", "arriba"): "Gira la cara derecha hacia arriba."
}

def cubo_resuelto():
    return {nombre: [COLOR_MAP[nombre]]*9 for nombre in FACE_NAMES}

def aplicar_movimiento(cube, move):
    c = copy.deepcopy(cube)
    # Demo visual: solo rota la cara correspondiente de forma horaria o antihoraria
    cara, direccion = move
    if direccion == "derecha" or direccion == "abajo":
        cube[cara] = [c[cara][6],c[cara][3],c[cara][0],c[cara][7],c[cara][4],c[cara][1],c[cara][8],c[cara][5],c[cara][2]]
    elif direccion == "izquierda" or direccion == "arriba":
        # antihorario: tres veces horario
        for _ in range(3):
            cube = aplicar_movimiento(cube, (cara, "derecha" if direccion == "izquierda" else "abajo"))
    return cube

def mezclar_cubo(n=6):
    cube = cubo_resuelto()
    mezcla = random.choices(MOVES, k=n)
    for mov in mezcla:
        cube = aplicar_movimiento(cube, mov)
    return cube, mezcla

def dibujar_cara(face, nombre):
    html = f"<b>{nombre}</b><br><table style='border-collapse:collapse;border:2px solid black;'>"
    for i in range(3):
        html += "<tr>"
        for j in range(3):
            color = COLOR_HEX[face[3*i+j]]
            html += f"<td style='background:{color};width:30px;height:30px;border:1px solid #444'></td>"
        html += "</tr>"
    html += "</table>"
    return html

def dibujar_cubo(cube):
    for nombre in FACE_NAMES:
        st.markdown(dibujar_cara(cube[nombre], nombre), unsafe_allow_html=True)

st.title("Rubik paso a paso - instrucciones didácticas")
st.caption("Siempre inicia desordenado y te guía un movimiento claro por paso.")

if "cube" not in st.session_state:
    cube, scramble = mezclar_cubo(7)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0

if st.button("Nuevo cubo desordenado"):
    cube, scramble = mezclar_cubo(7)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0
    st.experimental_rerun()

st.markdown("### Estado actual del cubo (6 caras)")
dibujar_cubo(st.session_state.cube)

if st.session_state.step < len(st.session_state.solve_seq):
    siguiente = st.session_state.solve_seq[st.session_state.step]
    st.info(f"Siguiente movimiento: {INSTRUCTIONS[siguiente]}")
    if st.button("Aplicar siguiente movimiento"):
        st.session_state.cube = aplicar_movimiento(st.session_state.cube, siguiente)
        st.session_state.step += 1
        st.experimental_rerun()
else:
    st.success("¡Cubo resuelto! Puedes mezclar de nuevo o experimentar.")

st.caption("Los movimientos y caras siempre aparecen con nombre completo y explicación sencilla.")