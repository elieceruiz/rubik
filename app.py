import streamlit as st
import random
import numpy as np

# Colores estándar por cara Rubik
FACE_COLORS = {
    "U": "white",   # Arriba
    "D": "yellow",  # Abajo
    "F": "green",   # Frente
    "B": "blue",    # Atrás
    "L": "orange",  # Izquierda
    "R": "red"      # Derecha
}

# Movimientos disponibles
ALL_MOVES = ["R", "Ri", "L", "Li", "U", "Ui", "D", "Di", "F", "Fi", "B", "Bi"]

MOVEMENT_EXPLAIN = {
    "R": "Gira la cara derecha en sentido horario",
    "Ri": "Gira la cara derecha en sentido antihorario",
    "L": "Gira la cara izquierda en sentido horario",
    "Li": "Gira la cara izquierda en sentido antihorario",
    "U": "Gira la cara superior en sentido horario",
    "Ui": "Gira la cara superior en sentido antihorario",
    "D": "Gira la cara inferior en sentido horario",
    "Di": "Gira la cara inferior en sentido antihorario",
    "F": "Gira la cara frontal en sentido horario",
    "Fi": "Gira la cara frontal en sentido antihorario",
    "B": "Gira la cara trasera en sentido horario",
    "Bi": "Gira la cara trasera en sentido antihorario",
}

# Inicializar cubo resuelto: cada cara es una lista de 9 colores
def get_face_colors():
    return {face: [FACE_COLORS[face]] * 9 for face in FACE_COLORS}

# Rotación realista de stickers en cada cara (solo R y Ri de ejemplo, puedes agregar otras)
def rotate_R(faces):
    # Girar stickers de la cara derecha
    old = faces["R"].copy()
    faces["R"][0], faces["R"][1], faces["R"][2], faces["R"][3], faces["R"][5], faces["R"][6], faces["R"][7], faces["R"][8] = old[6], old[3], old[0], old[7], old[1], old[8], old[5], old[2]
    # Girar stickers de las 4 adyacentes, simplificado
    f = faces["F"].copy()
    u = faces["U"].copy()
    b = faces["B"].copy()
    d = faces["D"].copy()
    faces["F"][2], faces["F"][5], faces["F"][8] = u[2], u[5], u[8]
    faces["U"][2], faces["U"][5], faces["U"][8] = b[6], b[3], b[0]
    faces["B"][0], faces["B"][3], faces["B"][6] = d[2], d[5], d[8]
    faces["D"][2], faces["D"][5], faces["D"][8] = f[2], f[5], f[8]
    return faces

def rotate_Ri(faces):
    # Girar R inversa (antihorario): aplicar horario 3 veces
    for _ in range(3):
        faces = rotate_R(faces)
    return faces

# Para este ejemplo, solo se implementan R y Ri, puedes añadir lógica para otros movimientos
ROTATION_FUNCS = {
    "R": rotate_R,
    "Ri": rotate_Ri,
    # Agregar aquí funciones similares para L, Li, U, Ui, D, Di, F, Fi, B, Bi
}

# Dibuja el cubo plano
def draw_flat_cube_html(faces):
    # Disposición clásica del cubo en 2D (U arriba, F centro, etc.)
    # Muestra cuadrícula en HTML para cada cara
    def draw_face(face):
        color_to_code = {"white":"#FFFFFF", "yellow":"#ffec00", "green":"#1eab39", "blue":"#0854aa", "orange":"#ff9900", "red":"#e6000a"}
        html = '<table style="border-collapse:collapse;border:2px solid black;">'
        for i in range(3):
            html += '<tr>'
            for j in range(3):
                c = face[3*i+j]
                html += f'<td style="background:{color_to_code[c]};width:24px;height:24px;border:1px solid #333"></td>'
            html += '</tr>'
        html += "</table>"
        return html
    st.markdown('<b>Cara superior (U)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["U"]), unsafe_allow_html=True)
    st.markdown('<b>Cara frontal (F)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["F"]), unsafe_allow_html=True)
    st.markdown('<b>Cara derecha (R)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["R"]), unsafe_allow_html=True)
    st.markdown('<b>Cara izquierda (L)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["L"]), unsafe_allow_html=True)
    st.markdown('<b>Cara inferior (D)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["D"]), unsafe_allow_html=True)
    st.markdown('<b>Cara trasera (B)</b>', unsafe_allow_html=True)
    st.markdown(draw_face(faces["B"]), unsafe_allow_html=True)

def main():
    st.title("Cubo Rubik plano - Amigable y simple")

    if "faces" not in st.session_state:
        st.session_state.faces = get_face_colors()
        scramble = random.choices(list(ROTATION_FUNCS.keys()), k=8)
        st.session_state.scramble = scramble
        st.session_state.step = 0

    if st.button("Generar nueva mezcla"):
        st.session_state.faces = get_face_colors()
        scramble = random.choices(list(ROTATION_FUNCS.keys()), k=8)
        st.session_state.scramble = scramble
        st.session_state.step = 0

    draw_flat_cube_html(st.session_state.faces)
    st.markdown(f"<b>Movimientos a realizar:</b> {' → '.join(st.session_state.scramble)}", unsafe_allow_html=True)

    # Mostrar cómo resolver, paso a paso
    if st.session_state.step < len(st.session_state.scramble):
        next_move = st.session_state.scramble[st.session_state.step]
        st.markdown(f"### Siguiente paso: {MOVEMENT_EXPLAIN[next_move]}")
        if st.button("Siguiente movimiento"):
            rot_func = ROTATION_FUNCS[next_move]
            st.session_state.faces = rot_func(st.session_state.faces)
            st.session_state.step += 1
    else:
        st.success("¡Has completado la secuencia!")

if __name__ == "__main__":
    main()