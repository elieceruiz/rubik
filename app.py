import streamlit as st
import random
import numpy as np
import plotly.graph_objects as go
from pymongo import MongoClient

# MongoDB conexión
mongo_uri = st.secrets["mongo_uri"]
client = MongoClient(mongo_uri)
db = client.rubikdb
collection = db.sessions

# Crear posiciones de 26 piezas del cubo Rubik visibles (excluye centro)
def create_positions():
    offset = 1.1
    positions = []
    for x in [-offset, 0, offset]:
        for y in [-offset, 0, offset]:
            for z in [-offset, 0, offset]:
                # Excluir posición central (0,0,0)
                if not (x == 0 and y == 0 and z == 0):
                    positions.append(np.array([x,y,z]))
    return positions

# Generar mezcla aleatoria de movimientos
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

# Rotar posiciones de piezas en 3D según movimiento simplificado
def rotar_piezas(positions, movimiento):
    angle = np.pi/2 if len(movimiento) == 1 else -np.pi/2
    axis = movimiento[0]
    
    def rotate(pos, axis, angle):
        x,y,z = pos
        if axis == "R" or axis == "L":
            # eje X
            y_new = y*np.cos(angle) - z*np.sin(angle)
            z_new = y*np.sin(angle) + z*np.cos(angle)
            x_new = x
        elif axis == "U" or axis == "D":
            # eje Y
            x_new = x*np.cos(angle) + z*np.sin(angle)
            z_new = -x*np.sin(angle) + z*np.cos(angle)
            y_new = y
        elif axis == "F" or axis == "B":
            # eje Z
            x_new = x*np.cos(angle) - y*np.sin(angle)
            y_new = x*np.sin(angle) + y*np.cos(angle)
            z_new = z
        else:
            x_new, y_new, z_new = x,y,z
        # Redondear para evitar error acumulado
        return np.array([round(x_new,2), round(y_new,2), round(z_new,2)])
    
    # Decidir qué piezas rotar según movimiento
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

# Visualizar cubo Rubik 3D con plotly
def plot_cubo(positions):
    fig = go.Figure()
    cube_size = 0.9
    for pos in positions:
        x,y,z = pos
        # Crear cubo como scatter3d de 8 vértices para cada pieza (simplificado como puntos)
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers',
            marker=dict(size=20, color='cyan', line=dict(width=2, color='black'))
        ))
    fig.update_layout(scene=dict(aspectmode='cube'))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

def main():
    st.title("Cubo Rubik 3D con Plotly - Aprendizaje interactivo")

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

    # Mostrar explicación del movimiento actual
    if st.session_state.indice < len(st.session_state.mezcla):
        mov = st.session_state.mezcla[st.session_state.indice]
        st.write(f"Movimiento actual: {mov}")
        st.write(explicacion.get(mov, "No hay explicación disponible"))
    else:
        st.success("¡Has completado la mezcla!")

    # Mostrar cubo 3D
    fig = plot_cubo(st.session_state.positions)
    st.plotly_chart(fig, use_container_width=True)

    # Botón para avanzar
    if st.button("Aplicar siguiente movimiento"):
        if st.session_state.indice < len(st.session_state.mezcla):
            movimiento = st.session_state.mezcla[st.session_state.indice]
            st.session_state.positions = rotar_piezas(st.session_state.positions, movimiento)
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