import streamlit as st
import random
import copy

# Nombres claros para cada cara
FACE_NAMES = {
    "U": "Arriba",
    "F": "Frontal",
    "R": "Derecha",
    "L": "Izquierda",
    "D": "Abajo",
    "B": "Atrás"
}
COLORS = {
    "Arriba": "white", "Frontal": "green", "Derecha": "red",
    "Izquierda": "orange", "Abajo": "yellow", "Atrás": "blue"
}
COLOR_HEX = {
    "white":"#FFFFFF", "yellow":"#ffec00", "green":"#1eab39",
    "blue":"#0854aa", "orange":"#ff9900", "red":"#e6000a"
}
MOVES = ["Derecha (hora)", "Derecha (anti)"]
EXPLAIN = {
    "Derecha (hora)": "Gira la cara derecha en sentido horario.",
    "Derecha (anti)": "Gira la cara derecha en sentido antihorario."
}

def cubo_resuelto():
    return {name: [color]*9 for name, color in COLORS.items()}

def move_Derecha_hora(cube):
    c = copy.deepcopy(cube)
    cube["Derecha"] = [c["Derecha"][6],c["Derecha"][3],c["Derecha"][0],
                       c["Derecha"][7],c["Derecha"][4],c["Derecha"][1],
                       c["Derecha"][8],c["Derecha"][5],c["Derecha"][2]]
    # Simplificado: solo giro visual en la cara
    return cube

def move_Derecha_anti(cube):
    for _ in range(3):
        cube = move_Derecha_hora(cube)
    return cube

ROTATION_FUNCS = {
    "Derecha (hora)": move_Derecha_hora,
    "Derecha (anti)": move_Derecha_anti
}

def mezclar_cubo(n=6):
    cube = cubo_resuelto()
    mezcla = random.choices(list(ROTATION_FUNCS.keys()), k=n)
    for mov in mezcla:
        cube = ROTATION_FUNCS[mov](cube)
    return cube, mezcla

def dibujar_cara(face, nombre):
    html = f"<b>{nombre}</b><br><table style='border-collapse:collapse;border:2px solid black;'>"
    for i in range(3):
        html += "<tr>"
        for j in range(3):
            color = COLOR_HEX[face[3*i+j]]
            html += f"<td style='background:{color};width:27px;height:27px;border:1px solid #444'></td>"
        html += "</tr>"
    html += "</table>"
    return html

def dibujar_cubo(cube):
    for name in ["Arriba","Frontal","Derecha","Izquierda","Abajo","Atrás"]:
        st.markdown(dibujar_cara(cube[name], name), unsafe_allow_html=True)

st.title("Rubik paso a paso - con nombres claros")

if "cube" not in st.session_state:
    cube, scramble = mezclar_cubo(6)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0

if st.button("Nuevo cubo aleatorio"):
    cube, scramble = mezclar_cubo(6)
    st.session_state.cube = cube
    st.session_state.scramble = scramble
    st.session_state.solve_seq = scramble[::-1]
    st.session_state.step = 0

st.markdown("### Estado actual del cubo (6 caras en plano)")
dibujar_cubo(st.session_state.cube)

if st.session_state.step < len(st.session_state.solve_seq):
    siguiente = st.session_state.solve_seq[st.session_state.step]
    st.info(f"Siguiente movimiento: {EXPLAIN[siguiente]}")
    if st.button("Aplicar siguiente movimiento"):
        st.session_state.cube = ROTATION_FUNCS[siguiente](st.session_state.cube)
        st.session_state.step += 1
        st.experimental_rerun()
else:
    st.success("¡Cubo resuelto! Puedes mezclar de nuevo o probar otro reto.")

st.caption("Todo el flujo usa nombres completos y explica cada giro de manera clara.")