import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random
import time
from pymongo import MongoClient

# Conexión MongoDB
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

def mezclar_cubo(posiciones, colores, pasos=8):
    history = [
        ("Gira la cara frontal a la derecha", "Frontal"),
        ("Gira la cara superior a la derecha", "Arriba"),
        ("Gira la cara derecha hacia arriba", "Derecha"),
        ("Gira la cara izquierda hacia arriba", "Izquierda"),
        ("Gira la cara abajo a la derecha", "Abajo"),
        ("Gira la cara trasera a la derecha", "Atrás"),
    ]
    movs = [random.choice(history) for _ in range(pasos)]
    return colores.copy(), movs

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

st.title("Rubik 3D didáctico, compacto, con pistas y MongoDB")

st.markdown(
    "<b>Caras del cubo:</b><br>" +
    "".join([f"- <span style='color:{hexa}'><b>{nombre}:</b> {color.capitalize()}</span><br>" for nombre, color, hexa in CARAS_INFO]),
    unsafe_allow_html=True
)

if (
    "cubo3d_pos" not in st.session_state
    or "cubo3d_col" not in st.session_state
    or "movs" not in st.session_state
):
    pos, col = cubo_resuelto()
    col, movs = mezclar_cubo(pos, col, pasos=6)
    st.session_state.cubo3d_pos = pos
    st.session_state.cubo3d_col = col
    st.session_state.movs = movs
    st.session_state.step = 0

if st.button("Nuevo cubo desordenado"):
    with st.spinner("Mezclando cubo..."):
        pos, col = cubo_resuelto()
        col, movs = mezclar_cubo(pos, col, pasos=6)
        st.session_state.cubo3d_pos = pos
        st.session_state.cubo3d_col = col
        st.session_state.movs = movs
        st.session_state.step = 0
    st.rerun()

st.plotly_chart(plot_cubo3d(st.session_state.cubo3d_pos, st.session_state.cubo3d_col), use_container_width=True)

st.markdown("#### Instrucción siguiente")
if st.session_state.step < len(st.session_state.movs):
    descripcion, cara_giro = st.session_state.movs[st.session_state.step]
    pasos_restantes = len(st.session_state.movs) - st.session_state.step
    if st.button("Aplicar este movimiento"):
        with st.spinner(f"Ejecutando: {descripcion}..."):
            time.sleep(0.7)
            nuevo_col = aplicar_giro(st.session_state.cubo3d_col, st.session_state.cubo3d_pos, cara_giro)
            st.session_state.cubo3d_col = nuevo_col
            st.session_state.step += 1
        st.rerun()
    st.info(f"{descripcion} ({pasos_restantes} pasos por resolver)")
else:
    st.success("¡Cubo resuelto! Mezcla de nuevo para otro reto.")

if st.button("Guardar estado actual en MongoDB"):
    with st.spinner("Guardando estado en base de datos..."):
        doc = {
            "colores":  st.session_state.cubo3d_col,
            "posiciones": st.session_state.cubo3d_pos,
            "mezcla": [mv[1] for mv in st.session_state.movs],
            "pasos_restantes": len(st.session_state.movs) - st.session_state.step
        }
        result = collection.insert_one(doc)
    st.success(f"Estado guardado en MongoDB (ID: {result.inserted_id})")

# requirements.txt:
# streamlit>=1.26.0
# plotly>=5.15.0
# numpy>=1.21.0
# pymongo>=4.3.3