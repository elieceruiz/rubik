import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random
import time
from pymongo import MongoClient

mongo_uri = st.secrets["mongo_uri"]
client = MongoClient(mongo_uri)
db = client.rubikdb
collection = db.cubos3d

CARAS_INFO = [
    ("Frontal", "green", "#1eab39"),
    ("Atrás", "blue", "#0854aa"),
    ("Arriba", "white", "#FFFFFF"),
    ("Abajo", "yellow", "#ffec00"),
    ("Izquierda", "orange", "#ff9900"),
    ("Derecha", "red", "#e6000a"),
]

# Instrucciones didácticas
INSTRUCCIONES = [
    ("Girar el borde derecho hacia el frente", "Derecha"),
    ("Girar el borde derecho hacia atrás", "Derecha"),
    ("Girar la cara frontal hacia la derecha", "Frontal"),
    ("Girar la cara frontal hacia la izquierda", "Frontal"),
    ("Girar la cara de atrás hacia la derecha", "Atrás"),
    ("Girar la cara de atrás hacia la izquierda", "Atrás"),
    ("Girar la cara izquierda hacia el frente", "Izquierda"),
    ("Girar la cara izquierda hacia atrás", "Izquierda"),
    ("Girar la cara inferior hacia la derecha", "Abajo"),
    ("Girar la cara inferior hacia la izquierda", "Abajo"),
    ("Girar la cara superior hacia la derecha", "Arriba"),
    ("Girar la cara superior hacia la izquierda", "Arriba"),
]

def crear_cubos():
    posiciones = []
    for x in [-1,0,1]:
        for y in [-1,0,1]:
            for z in [-1,0,1]:
                if not (x==0 and y==0 and z==0):
                    posiciones.append((x, y, z))
    return posiciones

def cubo_resuelto():
    posiciones = crear_cubos()
    colores = []
    for x, y, z in posiciones:
        if z == 1: color = "green"
        elif z == -1: color = "blue"
        elif y == 1: color = "white"
        elif y == -1: color = "yellow"
        elif x == 1: color = "red"
        elif x == -1: color = "orange"
        else: color = "gray"
        colores.append(color)
    return posiciones, colores

def aplicar_giro(cube_colors, posiciones, cara):
    colores = cube_colors.copy()
    if cara == "Frontal":
        idxs = [i for i, p in enumerate(posiciones) if p[2] == 1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (-p[1], p[0]))
    elif cara == "Atrás":
        idxs = [i for i, p in enumerate(posiciones) if p[2] == -1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (p[1], -p[0]))
    elif cara == "Arriba":
        idxs = [i for i, p in enumerate(posiciones) if p[1] == 1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (p[2], p[0]))
    elif cara == "Abajo":
        idxs = [i for i, p in enumerate(posiciones) if p[1] == -1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (-p[2], p[0]))
    elif cara == "Izquierda":
        idxs = [i for i, p in enumerate(posiciones) if p[0] == -1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (-p[1], p[2]))
    elif cara == "Derecha":
        idxs = [i for i, p in enumerate(posiciones) if p[0] == 1]
        cara_pos = [posiciones[i] for i in idxs]
        cara_grid = sorted(cara_pos, key=lambda p: (-p[1], -p[2]))
    else:
        return colores
    idxs_ord = [posiciones.index(p) for p in cara_grid]
    colores_cara = [colores[i] for i in idxs_ord]
    rotada = [colores_cara[6], colores_cara[3], colores_cara[0],
              colores_cara[7], colores_cara[4], colores_cara[1],
              colores_cara[8], colores_cara[5], colores_cara[2]]
    for k, idx in enumerate(idxs_ord):
        colores[idx] = rotada[k]
    return colores

def reorientar_amarillo_arriba(posiciones, colores):
    centros = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
    idx_amarillo = None
    for centro in centros:
        idx = posiciones.index(centro)
        if colores[idx] == "yellow":
            idx_amarillo = centro
            break
    if idx_amarillo is None or idx_amarillo == (0,1,0):
        return posiciones, colores
    if idx_amarillo == (0,-1,0):
        pos_nueva = [(x,-y,z) for x,y,z in posiciones]
        col_nueva = [colores[posiciones.index((x,-y,z))] for x,y,z in posiciones]
        return pos_nueva, col_nueva
    if idx_amarillo == (0,0,1):
        pos_nueva = [(x,z,-y) for x,y,z in posiciones]
        col_nueva = [colores[posiciones.index((x,z,-y))] for x,y,z in posiciones]
        return pos_nueva, col_nueva
    if idx_amarillo == (0,0,-1):
        pos_nueva = [(x,-z,y) for x,y,z in posiciones]
        col_nueva = [colores[posiciones.index((x,-z,y))] for x,y,z in posiciones]
        return pos_nueva, col_nueva
    if idx_amarillo == (1,0,0):
        pos_nueva = [(y,-x,z) for x,y,z in posiciones]
        col_nueva = [colores[posiciones.index((y,-x,z))] for x,y,z in posiciones]
        return pos_nueva, col_nueva
    if idx_amarillo == (-1,0,0):
        pos_nueva = [(-y,x,z) for x,y,z in posiciones]
        col_nueva = [colores[posiciones.index((-y,x,z))] for x,y,z in posiciones]
        return pos_nueva, col_nueva
    return posiciones, colores

def plot_cubo3d(posiciones, colores):
    fig = go.Figure()
    color_map = {
        'white':'#FFFFFF', 'yellow':'#ffec00', 'green':'#1eab39',
        'blue':'#0854aa', 'orange':'#ff9900', 'red':'#e6000a', 'gray':'#bab8b8'
    }
    size = 0.45
    for (x, y, z), color in zip(posiciones, colores):
        cube = go.Mesh3d(
            x=np.array([x-size, x+size, x+size, x-size, x-size, x+size, x+size, x-size]),
            y=np.array([y-size, y-size, y+size, y+size, y-size, y-size, y+size, y+size]),
            z=np.array([z-size, z-size, z-size, z-size, z+size, z+size, z+size, z+size]),
            color=color_map[color],
            opacity=1,
            i=[0, 0, 0, 7, 6, 5, 1, 2, 3, 4, 4, 1],
            j=[1, 2, 3, 6, 5, 4, 5, 6, 7, 7, 0, 5],
            k=[2, 3, 0, 5, 4, 1, 6, 7, 4, 3, 1, 2],
            flatshading=True,
            showscale=False,
        )
        fig.add_trace(cube)
    fig.update_layout(scene=dict(
        xaxis=dict(nticks=3, showbackground=False),
        yaxis=dict(nticks=3, showbackground=False),
        zaxis=dict(nticks=3, showbackground=False),
        aspectratio=dict(x=1, y=1, z=1),
    ),
    margin=dict(l=0, r=0, b=0, t=35),
    width=600,
    height=580)
    return fig

st.title("Rubik 3D con movimientos y instrucción didáctica")

st.markdown(
    "<b>Caras del cubo:</b><br>" +
    "".join([f"- <span style='color:{hexa}'><b>{nombre}:</b> {color.capitalize()}</span><br>" for nombre, color, hexa in CARAS_INFO]),
    unsafe_allow_html=True
)

if (
    "cubo3d_pos" not in st.session_state
    or "cubo3d_col" not in st.session_state
    or "movimientos" not in st.session_state
):
    pos, col = cubo_resuelto()
    movimientos = [random.choice(INSTRUCCIONES) for _ in range(random.randint(20,40))]
    for _, cara in movimientos:
        col = aplicar_giro(col, pos, cara)
    pos, col = reorientar_amarillo_arriba(pos, col)
    st.session_state.cubo3d_pos = pos
    st.session_state.cubo3d_col = col
    st.session_state.movimientos = movimientos
    st.session_state.paso = 0

if st.button("Nuevo cubo desordenado"):
    with st.spinner("Mezclando cubo y asegurando amarillo arriba..."):
        pos, col = cubo_resuelto()
        movimientos = [random.choice(INSTRUCCIONES) for _ in range(random.randint(20,40))]
        for _, cara in movimientos:
            col = aplicar_giro(col, pos, cara)
        pos, col = reorientar_amarillo_arriba(pos, col)
        st.session_state.cubo3d_pos = pos
        st.session_state.cubo3d_col = col
        st.session_state.movimientos = movimientos
        st.session_state.paso = 0
    st.rerun()

st.plotly_chart(plot_cubo3d(st.session_state.cubo3d_pos, st.session_state.cubo3d_col), use_container_width=True)

st.markdown("#### Paso didáctico")
if st.session_state.paso < len(st.session_state.movimientos):
    instruccion, cara_giro = st.session_state.movimientos[st.session_state.paso]
    pasos_restantes = len(st.session_state.movimientos) - st.session_state.paso
    if st.button("Aplicar este movimiento"):
        with st.spinner(f"Ejecutando: {instruccion}..."):
            time.sleep(0.7)
            nuevo_col = aplicar_giro(st.session_state.cubo3d_col, st.session_state.cubo3d_pos, cara_giro)
            st.session_state.cubo3d_col = nuevo_col
            st.session_state.paso += 1
        st.rerun()
    st.info(f"Instrucción: {instruccion} 
Quedan {pasos_restantes} movimientos por resolver")
else:
    st.success("¡Llegaste al final! Mezcla de nuevo para otro reto.")

if st.button("Guardar estado actual en MongoDB"):
    with st.spinner("Guardando estado en base de datos..."):
        doc = {
            "colores":  st.session_state.cubo3d_col,
            "posiciones": st.session_state.cubo3d_pos,
            "movimientos": st.session_state.movimientos,
            "paso_actual": st.session_state.paso
        }
        result = collection.insert_one(doc)
    st.success(f"Estado guardado en MongoDB (ID: {result.inserted_id})")