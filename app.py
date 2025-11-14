import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random
from pymongo import MongoClient

# Conexión MongoDB
mongo_uri = st.secrets["mongo_uri"]
client = MongoClient(mongo_uri)
db = client.rubikdb
collection = db.cubos3d

CARAS = [
    ("Frontal", "green"),
    ("Atrás", "blue"),
    ("Arriba", "white"),
    ("Abajo", "yellow"),
    ("Izquierda", "orange"),
    ("Derecha", "red"),
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
        if z == 1:
            color = "green"
        elif z == -1:
            color = "blue"
        elif y == 1:
            color = "white"
        elif y == -1:
            color = "yellow"
        elif x == 1:
            color = "red"
        elif x == -1:
            color = "orange"
        else:
            color = "gray"
        colores.append(color)
    return posiciones, colores

def mezclar_cubo(posiciones, colores, pasos=8):
    idxs = list(range(len(colores)))
    history = [
        ("Gira la cara superior a la derecha", "Arriba a la derecha"),
        ("Gira la cara derecha hacia arriba", "Derecha hacia arriba"),
        ("Gira la cara frontal a la derecha", "Frontal a la derecha"),
        ("Gira la cara izquierda hacia arriba", "Izquierda hacia arriba"),
        ("Gira la cara abajo a la derecha", "Abajo a la derecha"),
        ("Gira la cara trasera a la derecha", "Atrás a la derecha"),
    ]
    movs = []
    colores_cur = colores.copy()
    for _ in range(pasos):
        random.shuffle(idxs)
        colores_cur = [colores_cur[j] for j in idxs]
        mov = random.choice(history)
        movs.append(mov)
    return colores_cur, movs

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
    margin=dict(l=0,r=0,b=0,t=35),
    width=600,
    height=580)
    # Etiquetas didácticas
    fig.add_annotation(dict(font=dict(size=15),
                            x=0, y=1.2, z=1.2, text="Cara Arriba", showarrow=False, xanchor="left", yanchor="bottom"))
    fig.add_annotation(dict(font=dict(size=15),
                            x=0, y=-1.2, z=-1.2, text="Cara Abajo", showarrow=False, xanchor="left", yanchor="top"))
    fig.add_annotation(dict(font=dict(size=15),
                            x=0, y=1.2, z=-1.2, text="Cara Trasera", showarrow=False, xanchor="left", yanchor="top"))
    fig.add_annotation(dict(font=dict(size=15),
                            x=1.2, y=0, z=0, text="Derecha", showarrow=False))
    fig.add_annotation(dict(font=dict(size=15),
                            x=-1.2, y=0, z=0, text="Izquierda", showarrow=False))
    fig.add_annotation(dict(font=dict(size=15),
                            x=0, y=0, z=1.2, text="Frontal", showarrow=False))
    return fig

st.title("Rubik 3D didáctico, compacto y con MongoDB")

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
    pos, col = cubo_resuelto()
    col, movs = mezclar_cubo(pos, col, pasos=6)
    st.session_state.cubo3d_pos = pos
    st.session_state.cubo3d_col = col
    st.session_state.movs = movs
    st.session_state.step = 0

st.plotly_chart(plot_cubo3d(st.session_state.cubo3d_pos, st.session_state.cubo3d_col), use_container_width=True)

st.markdown("#### Instrucción siguiente")
if st.session_state.step < len(st.session_state.movs):
    descripcion, didactico = st.session_state.movs[st.session_state.step]
    pasos_restantes = len(st.session_state.movs) - st.session_state.step
    st.info(f"{descripcion} ({pasos_restantes} pasos por resolver)")
    if st.button("Aplicar este movimiento"):
        st.session_state.step += 1
else:
    st.success("¡Cubo resuelto! Mezcla de nuevo para otro reto.")

if st.button("Guardar estado actual en MongoDB"):
    doc = {
        "colores":  st.session_state.cubo3d_col,
        "posiciones": st.session_state.cubo3d_pos,
        "mezcla": [mv[1] for mv in st.session_state.movs],
        "pasos_restantes": len(st.session_state.movs) - st.session_state.step
    }
    result = collection.insert_one(doc)
    st.success(f"Estado guardado en MongoDB (ID: {result.inserted_id})")

# requirements.txt:
# streamlit>=1.18.0
# plotly>=5.15.0
# numpy>=1.21.0
# pymongo>=4.3.3