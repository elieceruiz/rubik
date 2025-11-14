import streamlit as st
import pyvista as pv
from stpyvista import stpyvista
from pymongo import MongoClient
import random
import numpy as np

# MongoDB conexión
mongo_uri = st.secrets["mongo_uri"]
client = MongoClient(mongo_uri)
db = client.rubikdb
collection = db.sessions

# Crear cubos pequeños que representan las 27 piezas del cubo Rubik (incluye centro e invisibles)
def create_cubo_piezas():
    piezas = []
    offset = 1.1
    for x in [-offset, 0, offset]:
        for y in [-offset, 0, offset]:
            for z in [-offset, 0, offset]:
                cube = pv.Cube(center=(x, y, z), x_length=1, y_length=1, z_length=1)
                piezas.append(cube)
    return piezas

# Rotar las piezas según movimiento dado (simplificación)
def rotar_piezas(piezas, movimiento):
    angle = 90
    axis_map = {
        "R": (1, 0, 0),
        "L": (-1, 0, 0),
        "U": (0, 1, 0),
        "D": (0, -1, 0),
        "F": (0, 0, 1),
        "B": (0, 0, -1),
    }
    axis = axis_map.get(movimiento[0], (0, 0, 0))
    sentido = 1 if len(movimiento) == 1 else -1

    for i, pieza in enumerate(piezas):
        if debe_rotar(pieza, movimiento[0]):  # Función para decidir qué piezas rotar según movimiento
            piezas[i] = pieza.rotate_vector(axis, angle * sentido, point=(0,0,0), inplace=False)
    return piezas

def debe_rotar(pieza, cara):
    # Función simplificada que debe determinar si una pieza pertenece a la cara que vamos a rotar según posición central
    # Por ejemplo, para cara R rotar todas con x > 0, etc.
    center = pieza.center
    if cara == "R":
        return center[0] > 0.9
    if cara == "L":
        return center[0] < -0.9
    if cara == "U":
        return center[1] > 0.9
    if cara == "D":
        return center[1] < -0.9
    if cara == "F":
        return center[2] > 0.9
    if cara == "B":
        return center[2] < -0.9
    return False

# Generar mezcla aleatoria de movimientos como ejemplo
def generar_mezcla(num=15):
    movimientos = ["R", "Ri", "L", "Li", "U", "Ui", "D", "Di", "F", "Fi", "B", "Bi"]
    return random.choices(movimientos, k=num)

# Explicación simplificada de movimientos
explicacion = {
    "R": "Gira la cara derecha en el sentido horario",
    "Ri": "Gira la cara derecha en sentido antihorario",
    "L": "Gira la cara izquierda en el sentido horario",
    "Li": "Gira la cara izquierda en sentido antihorario",
    "U": "Gira la cara superior en el sentido horario",
    "Ui": "Gira la cara superior en sentido antihorario",
    "D": "Gira la cara inferior en el sentido horario",
    "Di": "Gira la cara inferior en sentido antihorario",
    "F": "Gira la cara frontal en el sentido horario",
    "Fi": "Gira la cara frontal en sentido antihorario",
    "B": "Gira la cara trasera en el sentido horario",
    "Bi": "Gira la cara trasera en sentido antihorario",
}

def main():
    st.title("Cubo Rubik 3D - Aprendizaje interactivo")

    if "piezas" not in st.session_state:
        st.session_state.piezas = create_cubo_piezas()
    if "mezcla" not in st.session_state:
        st.session_state.mezcla = generar_mezcla()
        st.session_state.indice = 0
    
    st.sidebar.write(f"Paso actual: {st.session_state.indice} / {len(st.session_state.mezcla)}")
    st.sidebar.write(f"Movimientos faltantes: {len(st.session_state.mezcla) - st.session_state.indice}")
    
    if st.sidebar.button("Generar nueva mezcla"):
        st.session_state.piezas = create_cubo_piezas()
        st.session_state.mezcla = generar_mezcla()
        st.session_state.indice = 0

    # Mostrar explicación del movimiento actual
    if st.session_state.indice < len(st.session_state.mezcla):
        mov = st.session_state.mezcla[st.session_state.indice]
        st.write(f"Movimiento actual: {mov}")
        st.write(explicacion.get(mov, "No hay explicación disponible"))
    else:
        st.success("¡Has completado la mezcla!")

    # Mostrar cubo 3D
    plotter = pv.Plotter(window_size=[600, 600])
    for pieza in st.session_state.piezas:
        plotter.add_mesh(pieza, color="cyan", show_edges=True)
    plotter.view_isometric()
    plotter.background_color = "white"
    stpyvista(plotter)

    # Botón para avanzar
    if st.button("Aplicar siguiente movimiento"):
        if st.session_state.indice < len(st.session_state.mezcla):
            movimiento = st.session_state.mezcla[st.session_state.indice]
            st.session_state.piezas = rotar_piezas(st.session_state.piezas, movimiento)
            st.session_state.indice += 1
        else:
            st.success("Ya se aplicaron todos los movimientos.")

    # Guardar estado en MongoDB
    if st.button("Guardar estado actual"):
        estado = {
            "mezcla": st.session_state.mezcla,
            "indice": st.session_state.indice
        }
        collection.insert_one(estado)
        st.success("Estado guardado en MongoDB")

if __name__ == "__main__":
    main()
