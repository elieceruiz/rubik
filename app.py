import streamlit as st

color_options = ["white", "yellow", "green", "blue", "orange", "red"]
color_labels = {
    "white": "⬜ Blanco",
    "yellow": "🟨 Amarillo",
    "green": "🟩 Verde",
    "blue": "🟦 Azul",
    "orange": "🟧 Naranja",
    "red": "🟥 Rojo"
}

# Inicializa la cuadrícula de la cara superior (U)
if "face_grid" not in st.session_state:
    st.session_state.face_grid = [["white"]*3 for _ in range(3)]

st.title("Configura la cara superior (U) de tu cubo Rubik")

st.markdown("### Escoge el color de cada sticker de la cara de arriba, igual a tu cubo físico:")

for i in range(3):
    cols = st.columns(3)
    for j in range(3):
        current = st.session_state.face_grid[i][j]
        st.session_state.face_grid[i][j] = cols[j].selectbox(
            f"Sticker ({i+1},{j+1})", 
            options=color_options,
            format_func=lambda x: color_labels[x],
            index=color_options.index(current),
            key=f"sticker_{i}_{j}"
        )

st.markdown("### Vista previa de tu cara superior (U):")
def draw_face_grid(grid):
    color_hex = {"white":"#FFFFFF", "yellow":"#ffec00", "green":"#1eab39", 
                 "blue":"#0854aa", "orange":"#ff9900", "red":"#e6000a"}
    html = "<table style='border-collapse:collapse;border:2px solid black;'>"
    for i in range(3):
        html += "<tr>"
        for j in range(3):
            color = color_hex[grid[i][j]]
            html += f"<td style='background:{color};width:36px;height:36px;border:1px solid #333'></td>"
        html += "</tr>"
    html += "</table>"
    return html

st.markdown(draw_face_grid(st.session_state.face_grid), unsafe_allow_html=True)

# Aquí podrías almacenar, procesar o pasar este grid a resolver el cubo
if st.button("Guardar configuración de la cara superior"):
    st.success("¡Configuración guardada! Ahora puedes usar estos datos para guiar a la app o resolver paso a paso.")

st.info("Cuando pulses el botón guardar, puedes extender para completar las otras caras, o pasar a una lógica de solución.")

# Si quieres que este flujo se repita para otras caras (D, F, L, R, B), ajusta la misma lógica y guarda cada una como una variable en session_state.