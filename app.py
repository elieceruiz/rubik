import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random

# Nombres y colores
COLORS = ['green', 'blue', 'white', 'yellow', 'orange', 'red']
NAMES = ['Frontal', 'Atrás', 'Arriba', 'Abajo', 'Izquierda', 'Derecha']

def crear_cubo_resuelto():
    # Cada pieza tiene su color principal siguiendo el eje correspondiente
    cube = {}
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                if (x,y,z) != (0,0,0):
                    key = (x, y, z)
                    # Asignar color dominante según posición
                    if z == 1: color = 'green'
                    elif z == -1: color = 'blue'
                    elif y == 1: color = 'white'
                    elif y == -1: color = 'yellow'
                    elif x == 1: color = 'red'
                    elif x == -1: color = 'orange'
                    else: color = 'gray'
                    cube[key] = color
    return cube

def mezclar_cubo(cube, n=10):
    keys = list(cube.keys())
    colores = list(cube.values())
    for _ in range(n):
        random.shuffle(colores)
    mixed = dict(zip(keys, colores))
    return mixed

def plot_cubo3d(cube_dict):
    fig = go.Figure()
    colors_plotly = {
        'white':'#FFFFFF', 'yellow':'#ffec00', 'green':'#1eab39',
        'blue':'#0854aa', 'orange':'#ff9900', 'red':'#e6000a', 'gray':'#c1c1c1'
    }
    for key, color in cube_dict.items():
        x, y, z = key
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode='markers',
            marker=dict(size=22, color=colors_plotly[color], line=dict(width=1, color='black'))
        ))
    fig.update_layout(scene=dict(
        xaxis=dict(nticks=3, range=[-1.5,1.5], backgroundcolor="rgba(0,0,0,0)"),
        yaxis=dict(nticks=3, range=[-1.5,1.5], backgroundcolor="rgba(0,0,0,0)"),
        zaxis=dict(nticks=3, range=[-1.5,1.5], backgroundcolor="rgba(0,0,0,0)"),
        aspectratio=dict(x=1, y=1, z=1),
    ), margin=dict(l=0,r=0,b=0,t=25), width=520, height=520, title="Cubo Rubik 3D")
    return fig

st.title("Rubik 3D - Visualización simple y mezclada")

if st.button("Nuevo cubo desordenado") or "cube3d" not in st.session_state:
    base = crear_cubo_resuelto()
    st.session_state.cube3d = mezclar_cubo(base, 15)

fig = plot_cubo3d(st.session_state.cube3d)
st.plotly_chart(fig, use_container_width=True)

st.info("Cada esfera es una pieza. Pulsa el botón para mezclar de nuevo. ¿Quieres movimientos paso a paso y guardar/quitar piezas? Avísame.")