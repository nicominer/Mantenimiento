from datetime import datetime
from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gestión de Mantenimiento - Nicolás & Equipo",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Sistema de Mantenimiento - Nicolás, Matías, Jharry y Lucas")
st.markdown("Registro colaborativo con opción de edición y exportación a PDF.")

# Base de datos inicial colaborativa
if "df_mantenimiento" not in st.session_state:
  data_colaborativa = [
      {
          "Detalle": "CAMBIO DE DESLIZABLE LCAW DEL",
          "Máquina": "LEADER 1",
          "Fecha": "2026-01-02",
          "Técnico": "MATIAS",
          "Causa": "DESGASTE",
          "Tipo": "CORRECTIVO",
          "Categoría": "MECANICA",
      },
      {
          "Detalle": "CAMBIO DE GENERADOR ULTRASONIDO",
          "Máquina": "XB1",
          "Fecha": "2026-09-01",
          "Técnico": "JHARRY",
          "Causa": "FALLA",
          "Tipo": "CORRECTIVO",
          "Categoría": "ULTRASONIDO",
      },
      {
          "Detalle": "CAMBIO DE CORREA MOTOR CONFECION MANIJERA",
          "Máquina": "XB1",
          "Fecha": "2026-10-06",
          "Técnico": "LUCAS",
          "Causa": "CORTADA",
          "Tipo": "CORRECTIVO",
          "Categoría": "MECANICA",
      },
  ]
  st.session_state.df_mantenimiento = pd.DataFrame(data_colaborativa)

df = st.session_state.df_mantenimiento

# Función para generar PDF
def generar_pdf(dataframe):
  pdf = FPDF()
  pdf.add_page()
  pdf.set_font("Arial", "B", 14)
  pdf.cell(
      200, 10, txt="Informe de Mantenimiento - Planta", ln=True, align="C"
  )
  pdf.set_font("Arial", "", 10)
  pdf.cell(
      200,
      10,
      txt=f"Generado el: {datetime.today().strftime('%Y-%m-%d')}",
      ln=True,
      align="C",
  )
  pdf.ln(10)

  # Cabeceras de tabla
  pdf.set_font("Arial", "B", 9)
  pdf.cell(25, 8, "Fecha", 1)
  pdf.cell(30, 8, "Máquina", 1)
  pdf.cell(25, 8, "Técnico", 1)
  pdf.cell(25, 8, "Tipo", 1)
  pdf.cell(85, 8, "Detalle", 1)
  pdf.ln()

  pdf.set_font("Arial", "", 8)
  for _, row in dataframe.iterrows():
    pdf.cell(25, 7, str(row["Fecha"]), 1)
    pdf.cell(30, 7, str(row["Máquina"])[:15], 1)
    pdf.cell(25, 7, str(row["Técnico"]), 1)
    pdf.cell(25, 7, str(row["Tipo"]), 1)
    pdf.cell(85, 7, str(row["Detalle"])[:45], 1)
    pdf.ln()

  return pdf.output(dest="S").encode("latin1")


# Menú lateral
menu = [
    "📋 Ver Historial",
    "➕ Cargar Nuevo Mantenimiento",
    "✏️ Editar Registros Anteriores",
    "📊 Informes y PDF",
]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

if menu[0] in choice:
  st.header("📋 Planilla General Sincronizada")
  busqueda = st.text_input("🔍 Buscar por máquina, detalle o técnico...", "")
  if busqueda:
    df_visible = df[
        df.apply(
            lambda row: row.astype(str)
            .str.contains(busqueda, case=False)
            .any(),
            axis=1,
        )
    ]
  else:
    df_visible = df

  st.dataframe(df_visible, use_container_width=True)

elif menu[1] in choice:
  st.header("➕ Cargar Nuevo Mantenimiento")

  with st.form("form_colaborativo", clear_on_submit=True):
    col_u1, col_u2 = st.columns(2)
    with col_u1:
      # Tu nombre integrado (Nicolás) en lugar de administrador
      tecnico = st.selectbox(
          "¿Quién realiza la carga?", ["NICOLÁS", "MATIAS", "JHARRY", "LUCAS"]
      )
      maquina = st.selectbox(
          "Máquina / Equipo",
          [
              "XB1",
              "XB2",
              "XB3",
              "XB4",
              "XB5",
              "LEADER 1",
              "LEADER 2",
              "LEADER 3",
              "COMPRESOR SAAV. ADEL",
              "COMPRESOR SAAV. ATR",
              "FLEXO 4",
              "FLEXO 6",
              "FLEXO 8",
              "SERI",
              "MAQUINA DE TELA",
              "OTRO",
          ],
      )
      fecha = st.date_input("Fecha del Trabajo", datetime.today())

    with col_u2:
      tipo = st.selectbox(
          "Tipo", ["CORRECTIVO", "PREVENTIVO", "PREDICTIVO", "MEJORA"]
      )
      categoria = st.selectbox(
          "Categoría",
          [
              "MECANICA",
              "ELECTRICA",
              "NEUMATICA",
              "ELECTRONICA",
              "ULTRASONIDO",
              "ORDEN Y LIMPIEZA",
          ],
      )
      causa = st.text_input(
          "Causa del problema", placeholder="Ej. Desgaste, rotura..."
      )

    detalle = st.text_area(
        "Detalle del Trabajo Realizado",
        placeholder="Describa brevemente la tarea efectuada...",
    )

    submitted = st.form_submit_button("🚀 Enviar Registro")

    if submitted:
      if detalle.strip() == "":
        st.warning("Por favor ingresa el detalle del trabajo.")
      else:
        nuevo_registro = {
            "Detalle": detalle.upper(),
            "Máquina": maquina,
            "Fecha": str(fecha),
            "Técnico": técnico,
            "Causa": causa.upper() if causa else "-",
            "Tipo": tipo,
            "Categoría": categoria,
        }
        st.session_state.df_mantenimiento = pd.concat(
            [st.session_state.df_mantenimiento, pd.DataFrame([nuevo_registro])],
            ignore_index=True,
        )
        st.success(
            f"✅ ¡Registrado con éxito por **{tecnico}**! Disponible para"
            " todos."
        )

elif menu[2] in choice:
  st.header("✏️ Editar Registros Anteriores")
  st.markdown("Selecciona una fila del historial para modificar sus datos.")

  if not df.empty:
    # Mostramos la tabla con índices para que elijas cuál editar
    edit_index = st.number_input(
        "Número de Fila a Editar",
        min_value=0,
        max_value=len(df) - 1,
        step=1,
    )

    st.subheader(f"Editando Registro N° {edit_index}")
    row_actual = df.loc[edit_index]

    with st.form("form_edicion"):
      nuevo_detalle = st.text_input("Detalle", value=row_actual["Detalle"])
      nueva_maquina = st.text_input("Máquina", value=row_actual["Máquina"])
      nuevo_tecnico = st.selectbox(
          "Técnico",
          ["NICOLÁS", "MATIAS", "JHARRY", "LUCAS"],
          index=(
              ["NICOLÁS", "MATIAS", "JHARRY", "LUCAS"].index(
                  row_actual["Técnico"]
              )
              if row_actual["Técnico"]
              in ["NICOLÁS", "MATIAS", "JHARRY", "LUCAS"]
              else 0
          ),
      )
      nueva_causa = st.text_input("Causa", value=row_actual["Causa"])
      nuevo_tipo = st.selectbox(
          "Tipo",
          ["CORRECTIVO", "PREVENTIVO", "PREDICTIVO", "MEJORA"],
          index=(
              ["CORRECTIVO", "PREVENTIVO", "PREDICTIVO", "MEJORA"].index(
                  row_actual["Tipo"]
              )
              if row_actual["Tipo"]
              in ["CORRECTIVO", "PREVENTIVO", "PREDICTIVO", "MEJORA"]
              else 0
          ),
      )

      guardar_cambios = st.form_submit_button("💾 Guardar Cambios")

      if guardar_cambios:
        st.session_state.df_mantenimiento.at[edit_index, "Detalle"] = (
            nuevo_detalle.upper()
        )
        st.session_state.df_mantenimiento.at[edit_index, "Máquina"] = (
            nueva_maquina.upper()
        )
        st.session_state.df_mantenimiento.at[edit_index, "Técnico"] = (
            nuevo_tecnico
        )
        st.session_state.df_mantenimiento.at[edit_index, "Causa"] = (
            nueva_causa.upper()
        )
        st.session_state.df_mantenimiento.at[edit_index, "Tipo"] = nuevo_tipo
        st.success("¡Registro actualizado correctamente!")
  else:
    st.info("No hay registros para editar.")

elif menu[3] in choice:
  st.header("📊 Generación de Informes en PDF y Descargas")

  if not df.empty:
    st.markdown(
        "Filtra los datos que deseas exportar al informe PDF o en formato CSV:"
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
      tec_pdf = st.selectbox(
          "Filtrar por Técnico para el PDF",
          ["Todos"] + list(df["Técnico"].unique()),
      )
    with col_p2:
      maq_pdf = st.selectbox(
          "Filtrar por Máquina para el PDF",
          ["Todas"] + list(df["Máquina"].unique()),
      )

    df_pdf = df.copy()
    if tec_pdf != "Todos":
      df_pdf = df_pdf[df_pdf["Técnico"] == tec_pdf]
    if maq_pdf != "Todas":
      df_pdf = df_pdf[df_pdf["Máquina"] == maq_pdf]

    st.dataframe(df_pdf, use_container_width=True)

    # Botón de descarga de PDF
    pdf_bytes = generar_pdf(df_pdf)
    st.download_button(
        label="📥 Descargar Informe en Formato PDF",
        data=pdf_bytes,
        file_name="Informe_Mantenimiento.pdf",
        mime="application/pdf",
    )
  else:
    st.info("No hay datos disponibles para generar el informe.")
