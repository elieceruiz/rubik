import streamlit as st
import random
import numpy as np
import plotly.graph_objects as go
from pymongo import MongoClient

# --- CONFIGURACIÓN DE MONGODB ---
mongo_uri = st.secrets["mongo_uri"] # Tu uri secreta en Streamlit
client = MongoClient(mongo_uri)
db = client.rubikdb
collection = db.sessions

# --- CREAR POSICIONES DE 26 PIEZAS DEL CUBO (excluye centro interno) ---
def create_positions():
    offset = 1.1
    positions = []
    for x in [-offset, 0, offset]:
        for y in [-offset, 0, offset]:
            for z in [-offset, 0, offset]:
                if not (x == 0 and y == 0 and z == 0):
                    positions.append(np.array([x, y, z]))
    return positions

# --- ASIGNAR COLOR PRINCIPAL A CADA PIEZA SEGÚN CARA ---
def color_por_posicion(pos):
    x, y, z = pos
    if z > 0.9:
        return 'green'
    elif z < -0.9:
        return 'blue'
    elif y > 0.9:
        return 'white'
    elif y < -0.9:
        return 'yellow'
    elif x > 0.9:
        return 'red'
    elif x < -0.9:
        return 'orange'
    else:
        return 'gray'

# --- GENERAR MEZCLA DE MOVIMIENTOS ---
def generar_mezcla(num=15):
    movimientos = ["R", "Ri", "L", "Li", "U", "Ui", "D", "Di", "F", "Fi", "B", "Bi"]
    return random.choices(movimientos, k=num)

# --- TEXTO EXPLICATIVO DE CADA MOVIMIENTO ---
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

# --- ROTAR POSICIONES SEGÚN MOVIMIENTO ---
def rotar_piezas(positions, movimiento):
    angle = np.pi / 2 if len(movimiento) == 1 else -np.pi / 2
    axis = movimiento[0]

    def rotate(pos, axis, angle):
        x, y, z = pos
        if axis in ["R", "L"]:
            y_new = y * np.cos(angle) - z * np.sin(angle)
            z_new = y * np.sin(angle) + z * np.cos(angle)
            x_new = x
        elif axis in ["U", "D"]:
            x_new = x * np.cos(angle) + z * np.sin(angle)
            z_new = -x * np.sin(angle) + z * np.cos(angle)
            y_new = y
        elif axis in ["F", "B"]:
            x_new = x * np.cos(angle) - y * np.sin(angle)
            y_new = x * np.sin(angle) + y * np.cos(angle)
            z_new = z
        else:
            x_new, y_new, z_new = x, y, z
        return np.array([round(x_new, 2), round(y_new, 2), round(z_new, 2)])

    def debe_rotar(pos, cara):
        threshold = 0.9
        if cara == "R":
            return pos[0] > threshold
        if cara == "L":
            return pos[0] < -threshold
        if cara == "U":
            return pos[1] > threshold
        if cara == "D":
            return pos[1] < -threshold
        if cara == "F":
            return pos[2] > threshold
        if cara == "B":
            return pos[2] < -threshold
        return False

    new_positions = []
    for pos in positions:
        if debe_rotar(pos, axis):
            new_positions.append(rotate(pos, axis, angle))
        else:
            new_positions.append(pos)
    return new_positions

# --- VISUALIZAR CUBITO EN PLOTLY: CADA PIEZA COMO CUBO COMPLETO Y COLOR ---
def plot_cubo_caras(positions):
    fig = go.Figure()
    cube_size = 0.33
    for pos in positions:
        x, y, z = pos
        color = color_por_posicion(pos)
        # 8 vértices del cubo pequeño
        verts = np.array([
            [x-cube_size, y-cube_size, z-cube_size],
            [x+cube_size, y-cube_size, z-cube_size],
            [x+cube_size, y+cube_size, z-cube_size],
            [x-cube_size, y+cube_size, z-cube_size],
            [x-cube_size, y-cube_size, z+cube_size],
            [x+cube_size, y-cube_size, z+cube_size],
            [x+cube_size, y+cube_size, z+cube_size],
            [x-cube_size, y+cube_size, z+cube_size],
        ])
        # Caras del cubo (12 triángulos, simplificación para que se vea sólido)
        i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        j = [1, 3, 2, 6, 3, 7, 0, 4, 5, 1, 6, 2]
        k = [3, 7, 6, 5, 7, 6, 4, 0, 1, 5, 2, 6]
        fig.add_trace(go.Mesh3d(
            x=verts[:,0], y=verts[:,1], z=verts[:,2],
            color=color, opacity=0.9, flatshading=True,
            i=i, j=j, k=k, showscale=False
        ))
    fig.update_layout(scene=dict(aspectmode='cube'))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    return fig

# --- APP PRINCIPAL ---
def main():
    st.title("Cubo Rubik 3D - Caras completas pintadas")

    if "positions" not in st.session_state:
        st.session_state.positions = create_positions()
    if "mezcla" not in st.session_state:
        st.session_state.mezcla = generar_mezcla()
        st.session_state.indice = 0
    
    st.sidebar.write(f"Paso actual: {st.session_state.indice} / {len(st.session_state.mezcla)}")
    st.sidebar.write(f"Movimientos faltantes: {len(st.session_state.mezcla) - st.session_state.indice}")

    if st.sidebar.button("Generar nueva mezcla"):
        st.session_state.positions = create_positions()
        st.session_state.mezcla = generar_mezcla()
        st.session_state.indice = 0

    if st.session_state.indice < len(st.session_state.mezcla):
        mov = st.session_state.mezcla[st.session_state.indice]
        st.write(f"Movimiento actual: {mov}")
        st.write(explicacion.get(mov, "No hay explicación disponible"))
    else:
        st.success("¡Has completado la mezcla!")

    fig = plot_cubo_caras(st.session_state.positions)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Aplicar siguiente movimiento"):
        if st.session_state.indice < len(st.session_state.mezcla):
            movimiento = st.session_state.mezcla[st.session_state.indice]
            st.session_state.positions = rotar_piezas(st.session_state.positions, movimiento)
            st.session_state.indice += 1
        else:
            st.success("Ya se aplicaron todos los movimientos.")

    if st.button("Guardar estado actual"):
        estado = {
            "mezcla": st.session_state.mezcla,
            "indice": st.session_state.indice
        }
        collection.insert_one(estado)
        st.success("Estado guardado en MongoDB")

if __name__ == "__main__":
    main()