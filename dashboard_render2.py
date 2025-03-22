import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import re


# 📌 Cargar los datos desde archivos locales
# file_path_pronostico = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/Valores_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
# df_pronostico = pd.read_csv(file_path_pronostico, sep="\t")

url_pronostico = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/Valores_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
df_pronostico = pd.read_csv(url_pronostico, sep="\t")

# file_path_cambio_precipitacion = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/PorcentajesIndicesProbabilidad_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
# df_cambio_precipitacion = pd.read_csv(file_path_cambio_precipitacion, sep="\t")
url_cambio_precipitacion = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/PorcentajesIndicesProbabilidad_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
df_cambio_precipitacion = pd.read_csv(url_cambio_precipitacion, sep="\t")

# 📌 Archivos de Probabilidad
# file_path_superior = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/PorcentajesSuperior_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
# file_path_normal = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/PorcentajesNormal_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
# file_path_inferior = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/PorcentajesInferior_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
# file_path_indice = "C:/UNAL_MINMINAS/Blackboard/Lectura_archivos/IndicesProbabilidad_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
url_superior = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/PorcentajesSuperior_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
url_normal = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/PorcentajesNormal_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
url_inferior = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/PorcentajesInferior_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"
url_indice = "https://raw.githubusercontent.com/guzmar2010/dash_prediccion_v2/main/IndicesProbabilidad_Pronosticados_Precipitacion_Periodo_2025-2_a_2025-7_Colombia.csv"

# df_superior = pd.read_csv(file_path_superior, sep="\t")
# df_normal = pd.read_csv(file_path_normal, sep="\t")
# df_inferior = pd.read_csv(file_path_inferior, sep="\t")
# df_indice = pd.read_csv(file_path_indice, sep="\t")

df_superior = pd.read_csv(url_superior, sep="\t")
df_normal = pd.read_csv(url_normal, sep="\t")
df_inferior = pd.read_csv(url_inferior, sep="\t")
df_indice = pd.read_csv(url_indice, sep="\t")
# 📌 Unir archivos en un solo DataFrame
# 📌 Renombrar columnas agregando sufijo
for df, cat in zip([df_superior, df_normal, df_inferior, df_indice], ["3", "2", "1", "Índice"]):
    df.columns = [f"{col}.{cat}" if col not in ["Latitud", "Longitud", "Departamento", "Municipio"] else col for col in df.columns]
# 📌 Fusionar DataFrames en df_probabilidad
df_probabilidad = df_superior.merge(df_normal, on=["Latitud", "Longitud", "Departamento", "Municipio"])
df_probabilidad = df_probabilidad.merge(df_inferior, on=["Latitud", "Longitud", "Departamento", "Municipio"])
df_probabilidad = df_probabilidad.merge(df_indice, on=["Latitud", "Longitud", "Departamento", "Municipio"])

# 📌 Verificar que todas las categorías están presentes
print(df_probabilidad.columns.tolist())
print(df_probabilidad.head())
# 📌 Definir colores de las categorías
colores_categoria = {"1": "red", "2": "green", "3": "blue"}

# 📌 Identificar columnas de cambio porcentual
columnas_cambio = [col for col in df_cambio_precipitacion.columns if "2025-" in col]
columnas_temporales = [col for col in df_pronostico.columns if "2025-" in col]
# columnas_temporales_prob = [col for col in df_probabilidades.columns if "2025-" in col]
# 📌 Filtrar valores de -999
for col in columnas_temporales:
    df_pronostico = df_pronostico[df_pronostico[col] != -999]

# for col in columnas_temporales:
#     df_probabilidades = df_probabilidades[df_probabilidades[col] != -999]

for col in columnas_cambio:
    df_cambio_precipitacion = df_cambio_precipitacion[df_cambio_precipitacion[col] != -999]
# 📌 Definir escalas de colores
color_scale_pronostico = "RdBu"
color_scales_probabilidad = {3: "Blues", 2: "Greens", 1: "Reds"}
# 📌 Definir escala de colores personalizada
custom_color_scale = ["#8B0000", "#B22222", "#DC143C", "#FF4500", "#FFA500", "#FFFF00", "#9ACD32", "#32CD32", "#4682B4", "#4169E1", "#8A2BE2"]


# 📌 Inicializar Dash con Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
# app = dash.Dash(__name__,  suppress_callback_exceptions=True)
server = app.server  # Para despliegue
def convertir_mes(mes_texto):
    # Diccionario de conversión
    meses_dict = {
        "Mes 1": "Enero", "Mes 2": "Febrero", "Mes 3": "Marzo",
        "Mes 4": "Abril", "Mes 5": "Mayo", "Mes 6": "Junio",
        "Mes 7": "Julio", "Mes 8": "Agosto", "Mes 9": "Septiembre",
        "Mes 10": "Octubre", "Mes 11": "Noviembre", "Mes 12": "Diciembre"
    }
    
    # Retornar el nombre del mes si existe en el diccionario
    return meses_dict.get(mes_texto, mes_texto)  # Si no lo encuentra, retorna el mismo valor

# ✅ Estilos Globales
STYLE_CARD = {
    "border-radius": "10px",
    "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)", 
    "background-color":"#F0F0F0" ,  # ✅ Fondo blanco puro "#ffffff"
    "padding": "15px",
    "border": "none"  # ✅ Eliminando cualquier borde visible
}


STYLE_TEXT_CARD = {
    "border-radius": "12px",
    "box-shadow": "0px 4px 10px rgba(0, 0, 0, 0.15)",  # ✅ Sombras más sutiles
    "background-color": "#f8f9fa",  # ✅ Fondo gris claro para mejor contraste
    "padding": "24px",
    "font-size": "34px !important", #Tamaño de la fuente de 18px
    "font-weight": "bold",
    "color": "#333",
    "text-align": "center"
}


STYLE_FILTERS = {
    "background-color": "#f8f9fa",
    "border-radius": "10px",
    "padding": "22px",
    "box-shadow": "0px 4px 10px rgba(0, 0, 0, 0.2)",
    "font-size": "18px",
    "color": "black"
}

STYLE_TEXT = {
    "font-size": "18px",
    "line-height": "1.6",
    "font-weight": "500",
    "color": "#222"
}

# ✅ Encabezado con Logos
def create_navbar():
    return dbc.Navbar(
        dbc.Container([
            html.Img(src="/assets/gobierno.png", height="90px"),
            
            # Contenedor de título y texto adicional
            html.Div([
                html.H2("🌧️ Tablero de Predicción Climática para Colombia",
                        className="text-white fw-bold text-center",
                        style={"font-size": "36px", "margin-bottom": "5px"}),  # Ajuste de tamaño del título
                
                html.P("Análisis y visualización de las proyecciones mensuales de variables climáticas para la toma de decisiones", 
                       className="text-white text-center", 
                       style={"font-size": "22px", "margin-bottom": "0px"})  # Texto más pequeño
            ], className="flex-grow-1 text-center"),  # Centrado y ocupa el espacio restante

            # Contenedor de imágenes alineadas
            html.Div([
                html.Img(src="/assets/OAAS_cut.ico", height="90px"),
                html.Img(src="/assets/energia.png", height="90px")
            ], className="d-flex gap-3")  # d-flex para alinear y gap para separación
        ], fluid=True),
        
        color="dark", dark=True, className="mb-4 shadow",
        style={"background-color": "#343a40"}  # Gris oscuro
    )

# ✅ Pie de Página con Logos
def create_footer():
    return html.Footer([
        html.Div([
            html.Img(src="/assets/gobierno.png", height="80px"),
            html.Img(src="/assets/OAAS_cut.ico", height="80px"),
        ], className="d-flex justify-content-center"),
        html.P("Gobierno de Colombia - Todos los derechos reservados", 
                className="text-center mt-2 text-muted")
    ], className="bg-light p-3 mt-4",style={"background-color": "#eaeaea"})


# ✅ Diseño del Dashboard con Pestañas
app.layout = dbc.Container([
    create_navbar(),
    # ✅ Pestañas
    dcc.Tabs(id="tabs", value="tab1", children=[
        dcc.Tab(label="Pronóstico de Precipitación mensual", value="tab1",style={"font-size": "18px", "background-color": "#eaeaea", "color": "black"}),
        dcc.Tab(label="Probabilidades de Precipitación", value="tab2",style={"font-size": "18px", "background-color": "#eaeaea", "color": "black"}),
        dcc.Tab(label="Anomalia Porcentual de la Precipitación", value="tab3",style={"font-size": "18px", "background-color": "#eaeaea", "color": "black"})
        
    ], className="custom-tabs",style={"font-size": "18px"},colors={"border": "#cccccc", "primary": "#007bff", "background": "#f8f9fa"}),
    dcc.Store(id='store_relayout', storage_type='memory'),

    # ✅ Contenedor donde se renderiza el contenido dinámico de cada pestaña
    html.Div(id="tab_content"),
    create_footer()
], fluid=True, className="bg-light p-4 rounded shadow", style={"background-color": "#ffffff", "padding": "20px"})


@app.callback(
    Output('store_relayout', 'data'),
    Input('mapa_precipitacion', 'relayoutData'),
    prevent_initial_call=True
)
def guardar_relayout(relayout_data):
    if relayout_data and "mapbox.center" in relayout_data and "mapbox.zoom" in relayout_data:
        return {
            "center": relayout_data["mapbox.center"],
            "zoom": relayout_data["mapbox.zoom"]
        }
    return dash.no_update




# 📌 Callback para actualizar el contenido de las pestañas dinámicamente
@app.callback(
    Output('tab_content', 'children'),
    [Input('tabs', 'value')]
)
def update_tab(tab):
    # 📌 Extraer departamentos únicos
    departamentos_pronostico = sorted(df_pronostico["Departamento"].dropna().unique())
    departamentos_probabilidades = sorted(df_probabilidad["Departamento"].dropna().unique())
    departamentos_cambio = sorted(df_cambio_precipitacion["Departamento"].dropna().unique())

    if tab == 'tab1':  # Pestaña Pronóstico de Precipitación
        return dbc.Container([
            crear_filtros("selector_departamento", "selector_municipio", "selector_temporalidad", departamentos_pronostico, columnas_temporales),
            crear_fila_mapa_tarjeta("mapa_precipitacion", "texto_informativo"),
            crear_fila_grafico("grafico_precipitacion_mensual"),
            crear_fila_doble_grafico("histograma_pronostico"),
        ], fluid=True)

    elif tab == 'tab2':  # Pestaña Probabilidades de Precipitación
        return dbc.Container([                    
            crear_filtros("selector_departamento_probabilidades", "selector_municipio_probabilidades", "selector_temporalidad_prob", departamentos_probabilidades, [col for col in df_probabilidad.columns if '2025-' in col]),
            crear_fila_mapa_tarjeta("mapa_probabilidades", "texto_info_probabilidades"),
            crear_fila_grafico("grafico_distribucion_probabilidades"),
            crear_fila_grafico("grafico_comparacion_categorias")                       
        ], fluid=True)

    elif tab == 'tab3':  # Pestaña Cambio Porcentual de Precipitación
        return dbc.Container([
            # crear_filtros("selector_departamento_cambio", None, "selector_temporalidad_cambio", departamentos_cambio, columnas_cambio),
            crear_filtros("selector_departamento_cambio", "selector_municipio_cambio", "selector_temporalidad_cambio", departamentos_cambio, columnas_cambio),
            crear_fila_mapa_tarjeta("mapa_cambio_precipitacion", "texto_info_cambio"),
            crear_fila_grafico("grafico_cambio_mensual"),
        ], fluid=True)

    return html.Div()

# ✅ Función para crear filtros de selección
def crear_filtros(id_departamento, id_municipio, id_temporalidad, departamentos, columnas):
    return dbc.Row([
        dbc.Col([
            dmc.Text("🌍 Selecciona un Departamento", size="md", weight=500),
            dcc.Dropdown(
                id=id_departamento,
                options=[{"label": "🌎 Todos los Departamentos", "value": "Todos"}] +
                        [{"label": dep, "value": dep} for dep in departamentos],
                value="Todos",
                clearable=False,
                style={"width": "100%", "border-radius": "8px"}
            ),
        ], width=6 if id_municipio else 12),

        dbc.Col([
            dmc.Text("📅 Selecciona la Temporalidad", size="md", weight=500),
            dcc.Dropdown(
                id=id_temporalidad,
                options=[{"label": col.replace("2025-", "Mes "), "value": col} for col in columnas],
                value=columnas[0],
                clearable=False,
                style={"width": "100%", "border-radius": "8px"}
            ),
        ], width=6) if id_temporalidad else None,

        dbc.Col([
            dmc.Text("🏙️ Selecciona un Municipio", size="md", weight=500),
            dcc.Dropdown(
                id=id_municipio,
                clearable=True,
                placeholder="Selecciona un municipio",
                style={"width": "100%", "border-radius": "8px"}
            ),
        ], width=6) if id_municipio else None,
    ], className="mb-3 shadow-sm p-3", style=STYLE_FILTERS)

# ✅ Configuración global para los mapas
GRAPH_CONFIG = {
    "scrollZoom": True,
    "displaylogo": False,
    "displayModeBar": "hover"
}


# ✅ Función para crear fila con mapa y tarjeta de texto
def crear_fila_mapa_tarjeta(id_mapa, id_tarjeta):
    return dbc.Row([
        dbc.Col(dbc.Card(
            dcc.Loading(type="circle", children=dcc.Graph(id=id_mapa, config=GRAPH_CONFIG, clear_on_unhover=True)),
            body=True, className="shadow-sm p-2"), width=8),
        dbc.Col(dbc.Card([
            html.Div(id=id_tarjeta, className="text-center", style={"padding": "20px", "font-size": "20px"})
        ], body=True, className="shadow-sm p-3"), width=4)
    ], className="mb-4", align="stretch")

# ✅ Función para crear fila con un solo gráfico
def crear_fila_grafico(id_grafico):
    return dbc.Row([
        dbc.Col(dbc.Card(
            dcc.Loading(type="circle", children=dcc.Graph(id=id_grafico)),
            body=True, className="shadow-sm p-3"), width=12)
    ], className="mb-4", align="stretch")


# ✅ Función para crear una fila con uno o dos gráficos
def crear_fila_doble_grafico(id_grafico1, id_grafico2=None):
    if id_grafico2:  # Si se proporcionan dos gráficos
        return dbc.Row([
            dbc.Col(dbc.Card(
                dcc.Loading(type="circle", children=dcc.Graph(id=id_grafico1)),
                body=True, className="shadow-sm p-3"), width=6),
            dbc.Col(dbc.Card(
                dcc.Loading(type="circle", children=dcc.Graph(id=id_grafico2)),
                body=True, className="shadow-sm p-3"), width=6)
        ], className="mb-4", align="stretch")
    
    else:  # Si solo hay un gráfico
        return dbc.Row([
            dbc.Col(dbc.Card(
                dcc.Loading(type="circle", children=dcc.Graph(id=id_grafico1)),
                body=True, className="shadow-sm p-3"), width=12)
        ], className="mb-4", align="stretch")

#####################################################################################################################################################################
##################################################################PESTATAÑA PRONOSTICO#########################################################################
#####################################################################################################################################################################

# 📌 Callback para actualizar municipios en PRONÓSTICO#####
@app.callback(
    [Output("selector_municipio", "options"), Output("selector_municipio", "value")],
    [Input("selector_departamento", "value")]
)
def update_dropdown_options_municipio(departamento):
    if not departamento or departamento == "Todos":
        return [], None  

    municipios_filtrados = df_pronostico[df_pronostico["Departamento"].str.strip() == departamento.strip()]["Municipio"].dropna().unique()
    opciones_municipios = sorted([{"label": municipio, "value": municipio} for municipio in municipios_filtrados], key=lambda x: x["label"])

    return [{"label": "Todos los Municipios", "value": "Todos"}] + opciones_municipios, None


@app.callback(
    Output("selector_temporalidad", "options"),
    [Input("selector_departamento", "value")]
)
def update_temporalidad_options(departamento):
    opciones_temporalidad = [{"label": convertir_mes(col.replace("2025-", "Mes ")), "value": col} 
                             for col in columnas_temporales]
    return opciones_temporalidad


# 📌 Callback para actualizar el gráfico de pronóstico
@app.callback(
    [Output("mapa_precipitacion", "figure"), Output("histograma_pronostico", "figure")], #Output("violin_precipitacion", "figure")],
    [Input("selector_departamento", "value"), Input("selector_municipio", "value"),Input("selector_temporalidad", "value")],
    [State("store_relayout", "data")] 
)
def update_pronostico(departamento, municipio, temporalidad,relayout_store):
    df_filtrado_pronostico = df_pronostico.copy()

    # 📌 Aplicar filtros correctamente
    if departamento and departamento != "Todos":
        df_filtrado_pronostico = df_filtrado_pronostico[df_filtrado_pronostico["Departamento"] == departamento]

    if municipio and municipio != "Todos":
        df_filtrado_pronostico = df_filtrado_pronostico[df_filtrado_pronostico["Municipio"] == municipio]

    # 📌 Manejo de datos vacíos
    if df_filtrado_pronostico.empty:
        return px.scatter_mapbox(title="No hay datos disponibles"), px.histogram()#, px.violin()
    
    
    color_min_pronostico = df_filtrado_pronostico[temporalidad].min()
    color_max_pronostico = df_filtrado_pronostico[temporalidad].max()
    
    # global df_filtrado_pronostico
    # 📌 Generar Mapa de Pronóstico
    titulo_grafico5 = ""
    mes_texto = convertir_mes(temporalidad.replace("2025-", "Mes "))
    if departamento and departamento != "Todos":
          if municipio and municipio != "Todos":
              titulo_grafico5 = f"Mapa de Pronóstico de Precipitación mensual en {municipio}, {departamento} - {mes_texto}"
          else:
              titulo_grafico5 = f"Mapa de Pronóstico de Precipitación mensual en {departamento} - {mes_texto}"
    else:
          titulo_grafico5 = f"Mapa de Pronóstico de Precipitación mensual en Colombia - {mes_texto}"  
    columna_temporal = temporalidad
    fig_mapa = px.scatter_mapbox(
        df_filtrado_pronostico,
        lat="Latitud",
        lon="Longitud",
        size=temporalidad,
        color=temporalidad,
        size_max=10,
        hover_data= ["Latitud", "Longitud", "Departamento", "Municipio"],
        title=titulo_grafico5,
        # mapbox_style="carto-positron",
        mapbox_style="open-street-map",

        color_continuous_scale=color_scale_pronostico,
        range_color=[color_min_pronostico, color_max_pronostico],
        labels={temporalidad: f"Precipitación (mm)<br><sup>{convertir_mes(temporalidad.replace('2025-', 'Mes '))}"}


    )
    
   # 📌 Si hay relayoutData del gráfico anterior, usarlo para mantener el zoom y centro
    if relayout_store:
        try:
            center = relayout_store.get("center")
            zoom = relayout_store.get("zoom")
            if center and zoom:
               fig_mapa.update_layout(
                   mapbox=dict(
                        center={"lat": center["lat"], "lon": center["lon"]},
                        zoom=zoom,
                        style="open-street-map"
                   )
               )
        except Exception as e:
            print("⚠️ Error leyendo relayoutData:", e)
 
       
    
    
    fig_mapa.update_layout(
        title=dict(
            text=titulo_grafico5, 
            x=0.5, 
            y=0.95,
            xanchor="center", 
            yanchor="top",
            font=dict(size=20)  # Aumenta el tamaño del título
        ),
        mapbox=dict(
            center={"lat": df["Latitud"].mean(), "lon": df["Longitud"].mean()}, 
            zoom=4.3,
            style="open-street-map"
        ),
        height=750,  
        margin=dict(l=10, r=10, t=60, b=10)
    )
    mes_convertido = convertir_mes(temporalidad)
    mes_convertido = convertir_mes(temporalidad)

    fig_mapa.update_traces(
        hovertemplate = f"""
            <span style='font-size:14px; font-weight:bold;'>📍Municipio: %{{customdata[1]}}</span><br>
            <span style='font-size:14px;'>🌎 <b>Departamento:</b> %{{customdata[0]}}</span><br>
            <span style='font-size:14px;'>🧭 <b>Latitud:</b> %{{customdata[2]:.2f}}</span><br>
            <span style='font-size:14px;'>🧭 <b>Longitud:</b> %{{customdata[3]:.2f}}</span><br>
            <span style='font-size:14px;'>🌧️ <b>Precipitación ({mes_convertido}):</b> %{{customdata[4]:.1f}} mm</span><extra></extra>
            """,
        customdata = df_filtrado_pronostico[["Departamento", "Municipio", "Latitud", "Longitud", columna_temporal]].values
    )



    # 📌 Generar histogramas y gráficos adicionales
        
    titulo_grafico = ""
    mes_texto = convertir_mes(temporalidad.replace("2025-", "Mes "))
    if departamento and departamento != "Todos":
        if municipio and municipio != "Todos":
            titulo_grafico = f"Distribución de la precipitación mensual (%) en {municipio}, {departamento} - {mes_texto}"
        else:
            titulo_grafico = f"Distribución de la precipitación mensual (%) en {departamento} - {mes_texto}"
    else:
        titulo_grafico = f"Distribución de la precipitación mensual (%) en Colombia - {mes_texto}"  # Si no se selecciona nada
        
    
       
    fig_hist = px.histogram(df_filtrado_pronostico, x=temporalidad, nbins=20, histnorm='percent',
                            # title="Distribución de la Precipitación Pronosticada (%)",
                            title=titulo_grafico,
                            labels={temporalidad: "Precipitación (mm)", "percent": "Porcentaje"}, color_discrete_sequence=["#A9A9A9"])

   

    return fig_mapa, fig_hist 
#📌 Código para el Callback del Gráfico de Precipitación por Mes
@app.callback(
    Output("grafico_precipitacion_mensual", "figure"),
    [Input("selector_departamento", "value"), 
      Input("selector_municipio", "value"),Input("selector_temporalidad", "value")]
)
def update_grafico_mensual(departamento, municipio, temporalidad):
    df_filtrado = df_pronostico.copy()

    # 📌 Aplicar filtros por departamento y municipio
    if departamento and departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == departamento]

    if municipio and municipio != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Municipio"] == municipio]

    # 📌 Si el DataFrame está vacío después del filtrado, retornar gráfico vacío
    if df_filtrado.empty:
        return px.line(title="No hay datos disponibles")

    # 📌 Seleccionar solo las columnas de precipitación (2025-2, 2025-3, ..., 2025-7)
    columnas_temporales = [col for col in df_pronostico.columns if "2025-" in col]

    # 📌 Transformar la data de formato ancho a largo
    df_long = df_filtrado.melt(id_vars=["Departamento", "Municipio"], 
                                value_vars=columnas_temporales, 
                                var_name="Mes", value_name="Precipitación")

    # 📌 Renombrar las columnas de los meses (2025-2 → Mes 2)
    df_long["Mes"] = df_long["Mes"].str.replace("2025-", "Mes ")

    # 📌 Calcular promedio de precipitación por mes
    df_grouped = df_long.groupby("Mes")["Precipitación"].mean().reset_index()
    df_grouped["Mes"] = df_grouped["Mes"].apply(lambda x: convertir_mes(x))

    # 📌 Generar gráfico de líneas
   
    titulo_grafico6 = ""
    if departamento and departamento != "Todos":
          if municipio and municipio != "Todos":
              titulo_grafico6 = f"Pronóstico de la precipitación promedio por Mes en {municipio}, {departamento}"
          else:
              titulo_grafico6 = f"Pronóstico de la precipitación promedio por Mes en {departamento}"
    else:
          titulo_grafico6 = "Pronóstico de la precipitación promedio por Mes en Colombia"  # Si no se selecciona nada
    
    fig = px.line(df_grouped, x="Mes", y="Precipitación",
                  markers=True, line_shape="spline",
                  title=titulo_grafico6,
                  labels={"Mes": "Mes", "Precipitación": "Precipitación (mm)"},
                  color_discrete_sequence=["#007bff"])

    fig.update_layout(xaxis_title="Mes", yaxis_title="Precipitación (mm)", height=500)

    return fig

####📌Tarjeta de informacion junto al mapa de pronostico
@app.callback(
    Output("texto_informativo", "children"),
    [Input("selector_departamento", "value"), 
      Input("selector_municipio", "value"),
      Input("selector_temporalidad", "value")]
)
def update_texto_info(departamento, municipio, temporalidad):
    df_filtrado = df_pronostico.copy()

    if not departamento or departamento == "Todos":
        departamento = "Colombia"

    if departamento != "Colombia":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == departamento]
    
    if municipio and municipio not in [None, "Todos"]:
        df_filtrado = df_filtrado[df_filtrado["Municipio"] == municipio]

    if not df_filtrado.empty:
        promedio = df_filtrado[temporalidad].mean()
        # mes_texto = temporalidad.replace("2025-", "Mes ")
        mes_texto = convertir_mes(temporalidad.replace("2025-", "Mes "))


        if municipio in [None, "Todos"]:
            mensaje = [
                "📊 En ", html.B(departamento), 
                ", el promedio mensual de precipitación pronosticado para ", 
                html.B(mes_texto), " es de ", 
                html.B(f"{promedio:.2f} mm"), "."
            ]
        else:
            mensaje = [
                "📊 En el municipio de ", html.B(municipio), ", Departamento de ", html.B(departamento), 
                ", el promedio mensual de precipitación pronosticado para ", 
                html.B(mes_texto), " es de ", 
                html.B(f"{promedio:.2f} mm"), "."
            ]
    else:
        mensaje = "🔍 No hay datos disponibles para la selección actual."

    # ✅ **Nuevo diseño sin etiquetas <b> en texto crudo**
    return html.Div([
        html.P(["🌧️ ", html.B("Resumen del Pronóstico")], 
                style={"font-size": "34px", "text-align": "center", "font-weight": "bold", "color": "#333"}),

        html.P(mensaje, 
                style={"font-size": "30px", "text-align": "center", "margin-top": "10px"})
    ], style={
        "border-radius": "12px",
        "box-shadow": "0px 4px 10px rgba(0, 0, 0, 0.15)",
        "background-color": "#F8F9FA",
        "padding": "28px",
        "border": "4px solid #E5C100",
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",
        "flex-direction": "column"
    })
#####################################################################################################################################################################
##################################################################PESTATAÑA PROBABILIDAD#########################################################################
#####################################################################################################################################################################
# 📌 Callback para actualizar la lista de municipios en la pestaña de Probabilidad
@app.callback(
    [Output("selector_municipio_probabilidades", "options"), 
     Output("selector_municipio_probabilidades", "value")],
    [Input("selector_departamento_probabilidades", "value")]
)
def update_municipios_probabilidad(departamento):
    if not departamento or departamento == "Todos":
        return [], None  

    municipios_filtrados = df_probabilidad[df_probabilidad["Departamento"].str.strip() == departamento.strip()]["Municipio"].dropna().unique()
    opciones_municipios = sorted([{"label": municipio, "value": municipio} for municipio in municipios_filtrados], key=lambda x: x["label"])

    return [{"label": "Todos los Municipios", "value": "Todos"}] + opciones_municipios, None

# 📌 3️⃣ Callback para actualizar la lista de temporalidades en el selector
@app.callback(
    [Output("selector_temporalidad_prob", "options"),
    Output("selector_temporalidad_prob", "value")],
    [Input("selector_departamento_probabilidades", "value")]
)
def update_temporalidad_options(departamento):
    opciones_temporalidad = [{"label": convertir_mes(col.replace("2025-", "Mes ")), "value": col} 
                             for col in columnas_temporales]
    return opciones_temporalidad, opciones_temporalidad[0]["value"]

# 📌 Callback para actualizar el mapa de probabilidades
@app.callback(
    [Output("mapa_probabilidades", "figure"), 
      Output("texto_info_probabilidades", "children"),
      Output("grafico_distribucion_probabilidades", "figure")],
    [Input("selector_departamento_probabilidades", "value"),
      Input("selector_municipio_probabilidades", "value"),
      Input("selector_temporalidad_prob", "value")]
)  
def update_mapa_probabilidad(departamento, municipio, temporalidad_prob):
    df_filtrado = df_probabilidad.copy()
    print(df_filtrado.columns.tolist())

 # 📌 Validar que temporalidad no sea None
    if not temporalidad_prob:
        temporalidad_prob = sorted([col.split(".")[0] for col in df_probabilidad.columns if col.startswith("2025-")])[0]
        print(f"⚠ No se seleccionó una temporalidad. Usando {temporalidad_prob} por defecto.")

    # 📌 Filtrar por Departamento y Municipio
    if departamento and departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == departamento]

    if municipio and municipio != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Municipio"] == municipio]

    # 📌 Verificar si hay datos después de filtrar
    if df_filtrado.empty:
        print("⚠ No hay datos después de filtrar por Departamento/Municipio")
        return px.scatter_mapbox(title="No hay datos disponibles"), "🔍 No hay datos disponibles", px.line()

    # 📌 Construcción de las columnas de probabilidad por categoría
    categorias = {"1": "Por debajo", "2": "Normal", "3": "Por encima"}
    columnas_probabilidad = {cat: f"{temporalidad_prob}.{key}" for key, cat in categorias.items()}
    columnas_existentes = {cat: col for cat, col in columnas_probabilidad.items() if col in df_filtrado.columns}

    if not columnas_existentes:
        return px.scatter_mapbox(title="No hay datos disponibles")


    # 📌 Determinar la categoría dominante en cada punto
    df_filtrado["Categoría Dominante"] = df_filtrado[list(columnas_existentes.values())].idxmax(axis=1)
    df_filtrado["Categoría Dominante"] = df_filtrado["Categoría Dominante"].str.extract(r"(\d)$")[0].map(categorias)

    # 📌 Asignar colores a cada categoría
    colores_categoria = {"Por debajo": "#D73027", "Normal": "#91CF60", "Por encima": "#4575B4"}
    df_filtrado["Color"] = df_filtrado["Categoría Dominante"].map(colores_categoria)

    # 📌 Agregar valores de cada categoría para mostrar en hover
    for cat, col in columnas_existentes.items():
        df_filtrado[cat] = df_filtrado[col]
        
     # 📌 Crear mapa de probabilidades
    titulo_grafico3 = ""
    mes_texto = convertir_mes(temporalidad_prob.replace("2025-", "Mes "))
    if departamento and departamento != "Todos":
          if municipio and municipio != "Todos":
              titulo_grafico3 = f"Mapa de Probabilidades de que la Precipitación esté <br> por encima, igual o por debajo de lo normal en <br>{municipio}, {departamento} - {mes_texto} "
              
          else:
              titulo_grafico3 = f"Mapa de Probabilidades de que la Precipitación este <br> por encima, igual o por debajo de lo normal en \n{departamento} - {mes_texto} "
    else:
          titulo_grafico3 = f"Mapa de Probabilidades de que la Precipitación este <br> por encima, igual o por debajo de lo normal en Colombia - {mes_texto}"  # Si no se selecciona nada
    
    
    fig_mapa = px.scatter_mapbox(
        df_filtrado,
        lat="Latitud",
        lon="Longitud",
        color="Categoría Dominante",
        # size="Tamaño",
        hover_data={
            "Latitud": True, 
            "Longitud": True, 
            "Departamento": True, 
            "Municipio": True,
            "Por debajo": True,
            "Normal": True,
            "Por encima": True
        },
        title=titulo_grafico3,
        mapbox_style="open-street-map",
        color_discrete_map=colores_categoria,
        category_orders={"Categoría Dominante": ["Por debajo", "Normal", "Por encima"]} 
        
    )

            
    fig_mapa.update_layout(
    title=dict(
        text=titulo_grafico3, 
        x=0.5, 
        y=0.97, 
        xanchor="center", 
        yanchor="top",
        font=dict(size=20)
    ),
    # title_font_size=16,
    mapbox=dict(
        center={"lat": df_filtrado["Latitud"].mean(), "lon": df_filtrado["Longitud"].mean()}, 
        zoom=4.3
        
    ),
    height=750,
    margin=dict(l=10, r=10, t=85, b=10),
    legend_title_text="Categoría"
    
    
    )

    # 📌 Crear la tarjeta de información
    promedios = {cat: df_filtrado[cat].mean() for cat in categorias.values()}
    categoria_dominante = max(promedios, key=promedios.get)
    valor_dominante = promedios[categoria_dominante]

    iconos = {"Inferior": "🔴", "Normal": "🟢", "Superior": "🔵"}
    icono_categoria = iconos.get(categoria_dominante, "⚪")

    # 📌 Crear la figura de probabilidades acumuladas
    df_grouped = df_filtrado.groupby("Departamento" if departamento == "Todos" else "Municipio")[["Por debajo", "Normal", "Por encima"]].mean().reset_index()

    df_grouped["Total"] = df_grouped["Por debajo"] + df_grouped["Normal"] + df_grouped["Por encima"]
    for cat in categorias.values():
        df_grouped[cat] = ((df_grouped[cat] / df_grouped["Total"]) * 100).round(1)
    
     
     # 📌 Crear la tarjeta de información
    promedios = {cat: df_filtrado[cat].mean() for cat in categorias.values()}
    categoria_dominante = max(promedios, key=promedios.get)
    valor_dominante = promedios[categoria_dominante]
    
    iconos = {"Por debajo": "🔴", "Normal": "🟢", "Por encima": "🔵"}
    icono_categoria = iconos.get(categoria_dominante, "⚪")
    
    # 📌 Definir la ubicación del mensaje
    if not departamento or departamento == "Todos":
        ubicacion = "Colombia"
    elif departamento != "Todos" and (not municipio or municipio == "Todos"):
        ubicacion = f"el departamento de {departamento}"
    else:
        ubicacion = f"el municipio de {municipio}, Departamento de {departamento}"

    # 📌 Formatear mensaje con el nuevo formato
    # temporalidad = temporalidad_prob.replace("2025-", "Mes ")
    mensaje = [
        f"{icono_categoria} En ", html.B(ubicacion),
        ", la categoría más probable en ", html.B(mes_texto),
        " es ", html.B(categoria_dominante),
        " con un porcentaje promedio de ", html.B(f"{valor_dominante:.2f}%"), "."
    ]
    
   
    tarjeta_info_prob = html.Div([
            html.P("📊 Probabilidad de Precipitación",
                   style={"font-size": "34px", "font-weight": "bold", "color": "#333", "text-align": "center"}),  
            html.P(mensaje, 
                   style={"font-size": "32px", "text-align": "center", "margin-top": "12px"})
        ], 
        style={
            "border-radius": "12px",
            "box-shadow": "0px 4px 10px rgba(0, 0, 0, 0.15)",
            "background-color": "#F8F9FA",
            "padding": "28px",
            "border": "4px solid #E5C100",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "flex-direction": "column"
        }
    )
       
        
    ####Titutlo
    titulo_grafico4 = ""
    if departamento and departamento != "Todos":
         if municipio and municipio != "Todos":
             titulo_grafico4 = f"Probabilidad promedio de que la Precipitación este por encima, igual o por debajo de lo normal en {municipio}, {departamento} - {mes_texto}"
         else:
             titulo_grafico4 = f"Probabilidad promedio de que la Precipitación este por encima, igual o por debajo de lo normal en {departamento} - {mes_texto}"
    else:
         titulo_grafico4 = f"Probabilidad promedio de que la Precipitación este por encima, igual o por debajo de lo normal en Colombia - {mes_texto}"  # Si no se selecciona nada
   
    fig_bar_prob = px.bar(
        df_grouped,
        x="Departamento" if departamento == "Todos" else "Municipio",
        y=["Por debajo", "Normal", "Por encima"],
        barmode="stack",
        title=titulo_grafico4,
        labels={"value": "Probabilidad (%)", "variable": "Categoría"},
        color_discrete_map=colores_categoria,
        category_orders={"Categoría": ["Por debajo", "Normal", "Por encima"]} 
    )

    fig_bar_prob.update_layout(
        xaxis_title="Departamento" if departamento == "Todos" else "Municipio",
        yaxis_title="Probabilidad (%)",
        height=500
    )

    return fig_mapa, tarjeta_info_prob, fig_bar_prob
#################Grafico temporal de probabilidad
@app.callback(
    Output("grafico_comparacion_categorias", "figure"),
    [
        Input("selector_departamento_probabilidades", "value"),
        Input("selector_municipio_probabilidades", "value"),
        Input("selector_temporalidad_prob", "value")
    ]
)
def update_grafico_comparacion(departamento, municipio, temporalidad_prob):
    df_filtrado = df_probabilidad.copy()

    # 📌 Aplicar filtro por Departamento
    if departamento and departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == departamento]

    # 📌 Revisar si el DataFrame está vacío después del filtro
    print("📌 Registros después de filtrar por municipio:", len(df_filtrado))
    if df_filtrado.empty:
        print("⚠ No hay datos después de aplicar los filtros")
        return px.bar(title="No hay datos disponibles para los filtros seleccionados")

    # 📌 Extraer solo las columnas de temporalidad con sufijos .1, .2, .3 (sin índice)
    
    columnas_temporalidad = [
        col for col in df_filtrado.columns 
        if re.match(r"2025-\d+\.[123]$", col)  # Asegura que coincida con el formato esperado
    ]

    # 📌 Transformar a formato largo
    df_long = df_filtrado.melt(id_vars=["Departamento", "Municipio"], 
                                value_vars=columnas_temporalidad, 
                                var_name="Mes", value_name="Probabilidad")
    # global df_long
    # 📌 Extraer el número de mes y la categoría
    df_long["Categoría"] = df_long["Mes"].str.extract(r"\.(\d)$")[0]
    df_long["Mes"] = df_long["Mes"].str.replace(r"\.\d$", "", regex=True)

    # 📌 Mapear categorías numéricas a nombres
    df_long["Categoría"] = df_long["Categoría"].astype(str).map({"1": "Por debajo", "2": "Normal", "3": "Por encima"})

    # 📌 Convertir Probabilidad a numérico
    df_long["Probabilidad"] = pd.to_numeric(df_long["Probabilidad"], errors="coerce")

    # 📌 Filtrar valores nulos (evita errores)
    df_long = df_long[(df_long["Probabilidad"] != -999) & df_long[["Probabilidad", "Categoría", "Mes"]].notna().all(axis=1)]

    # 📌 Revisar si hay datos después de limpiar
    if df_long.empty:
        print("⚠ No hay datos después del procesamiento")
        return px.bar(title="No hay datos disponibles después del procesamiento")

    # 📌 Agrupar por Mes y Categoría, obteniendo el promedio
    df_grouped = df_long.groupby(["Mes", "Categoría"], as_index=False)["Probabilidad"].mean()
    # global df_long
    # 📌 Normalizar para que cada mes sume 100%
    df_grouped["Probabilidad"] = df_grouped.groupby("Mes")["Probabilidad"].transform(lambda x: (x / x.sum()) * 100)
  
    df_grouped["Mes"] = df_grouped["Mes"].apply(lambda x: convertir_mes(x.replace("2025-", "Mes ")))

    # 📌 Verificar si hay datos antes de graficar
    if df_grouped.empty:
        print("⚠ No hay datos disponibles para graficar")
        return px.bar(title="No hay datos disponibles para graficar")

    # # 📌 Manejo de temporalidad_prob si es None
    if not temporalidad_prob:
        temporalidad_prob = ""
    
    
    if departamento and departamento != "Todos":
        if municipio and municipio != "Todos":
              titulo_grafico7 = f"Histogramas de las probabilidades de que la precipitación este <br> por encima, igual o por debajo de lo normal, para los próximos seis meses en {municipio}, {departamento}"
        else:
              titulo_grafico7 = f"Histogramas de las probabilidades de que la precipitación este  <br> por encima, igual o por debajo de lo normal, para los próximos seis meses en {departamento}"
    else:
        titulo_grafico7 = "Histogramas de las probabilidades de que la precipitación este  <br> por encima, igual o por debajo de lo normal, para los próximos seis meses en Colombia"

    # 📌 Graficar con Plotly
    fig_comparacion = px.bar(
        df_grouped,
        x="Mes",
        y="Probabilidad",
        color="Categoría",
        barmode="group",
        title= titulo_grafico7,
        labels={"Mes": "Mes", "Probabilidad": "Probabilidad (%)", "Categoría": "Categoría"},
        color_discrete_map={"Por debajo": "#D73027", "Normal": "#91CF60", "Por encima": "#4575B4"},
        category_orders={"Categoría": ["Por debajo", "Normal", "Por encima"]} 
    )

    fig_comparacion.update_layout(
        title={
        "text": titulo_grafico7,  # Tu título dinámico
        "x": 0.5,  # Centra horizontalmente
        "y": 0.95,  # Ajusta la posición vertical (opcional)
        "xanchor": "center",  # Ancla en el centro
        "yanchor": "top",  # Mantiene el título arriba
        },
        xaxis_title="Mes",
        yaxis_title="Probabilidad (%)",
        height=500
    )

    return fig_comparacion



#####################################################################################################################################################################
##################################################################PESTATAÑA ANOMALIA PORCENTUAL#########################################################################
#####################################################################################################################################################################



 #📌 Callback para actualizar la lista de municipios en la pestaña de Cambio Porcentual
@app.callback(
    [Output("selector_municipio_cambio", "options"), Output("selector_municipio_cambio", "value")],
    [Input("selector_departamento_cambio", "value")]
)
def update_municipios_cambio(departamento):
    if not departamento or departamento == "Todos":
        return [], None  

    municipios_filtrados = df_cambio_precipitacion[df_cambio_precipitacion["Departamento"].str.strip() == departamento.strip()]["Municipio"].dropna().unique()
    opciones_municipios = sorted([{"label": municipio, "value": municipio} for municipio in municipios_filtrados], key=lambda x: x["label"])

    return [{"label": "Todos los Municipios", "value": "Todos"}] + opciones_municipios, None

@app.callback(
    Output("selector_temporalidad_cambio", "options"),
    Input("selector_departamento_cambio", "value")
)

def update_temporalidad_options(departamento):
    opciones_temporalidad = [{"label": convertir_mes(col.replace("2025-", "Mes ")), "value": col} 
                             for col in columnas_temporales]
    return opciones_temporalidad
 #📌 Callback para GRAFICOS  pestaña de Cambio Porcentual

@app.callback(
    [Output("mapa_cambio_precipitacion", "figure"), 
     Output("texto_info_cambio", "children"), 
     Output("grafico_cambio_mensual", "figure")],
    [Input("selector_departamento_cambio", "value"),
     Input("selector_municipio_cambio", "value"),
     Input("selector_temporalidad_cambio", "value")]
)
def update_cambio_precipitacion(departamento, municipio, temporalidad_cambio):
    df_filtrado = df_cambio_precipitacion.copy()

    if departamento in [None, "Todos"]:
        departamento = "Colombia"
    
    if municipio in [None, "Todos"]:
        municipio = None

    # 📌 Filtrar datos según selección
    if departamento != "Colombia":
        df_filtrado = df_filtrado[df_filtrado["Departamento"] == departamento]
    
    if municipio:
        df_filtrado = df_filtrado[df_filtrado["Municipio"] == municipio]

    # 📌 Si el dataframe está vacío, retornar valores predeterminados
    if df_filtrado.empty:
        return px.scatter_mapbox(title="No hay datos disponibles"), "🔍 No hay datos disponibles", px.line()

    # 📌 Calcular el cambio porcentual promedio
    promedio = df_filtrado[temporalidad_cambio].mean()
    # mes_texto = convertir_mes(temporalidad_cambio.replace("2025-", "Mes"))
    mes_texto = convertir_mes(f"Mes {temporalidad_cambio.replace('2025-', '')}")



    # 📌 Mensaje formateado
    if municipio is None:
        mensaje = [
            "📊 En ", html.B(departamento),
            ", la anomalia porcentual promedio de precipitación para ",
            html.B(mes_texto), " es de ",
            html.B(f"{promedio:.2f}%"), "."
        ]
    else:
        mensaje = [
            "📊 En el municipio de ", html.B(municipio), ", Departamento de ", html.B(departamento),
            ", la anomalia porcentual promedio de precipitación para ",
            html.B(mes_texto), " es de ",
            html.B(f"{promedio:.2f}%"), "."
        ]

    # 📌 Tarjeta de Información
    tarjeta_info_cambio = html.Div([
            html.P(["📉 ", html.B("Anomalia Porcentual de Precipitación")], 
                   style={"font-size": "34px", "font-weight": "bold", "color": "#333", "text-align": "center"}),

            html.P(mensaje, 
                   style={"font-size": "32px", "text-align": "center", "margin-top": "12px"}),

        ], 
        style={
            "border-radius": "12px",
            "box-shadow": "0px 4px 10px rgba(0, 0, 0, 0.15)",
            "background-color": "#F8F9FA",
            "padding": "28px",
            "border": "4px solid #E5C100",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "flex-direction": "column"
        }
    )

    # 📌 Gráfico de Cambio Porcentual
    titulo_mapa = ""
    if departamento and departamento != "Todos":
              if municipio and municipio != "Todos":
                  titulo_mapa = f"Mapa de la anomalia porcentual en {municipio}, {departamento} - {mes_texto}"
              else:
                  titulo_mapa = f"Mapa de la anomalia porcentual en {departamento} - {mes_texto}"
    else:
              titulo_mapa = f"Mapa de la anomalia porcentual en Colombia - {mes_texto}"
    
    fig_mapa = px.scatter_mapbox(
        df_filtrado,
        lat="Latitud",
        lon="Longitud",
        size=temporalidad_cambio,
        color=temporalidad_cambio,
        title=titulo_mapa,
        mapbox_style="open-street-map",
        color_continuous_scale="RdYlGn",
        labels={temporalidad_cambio: f"Porcentaje (%)<br><sup>{mes_texto}"},
        size_max=10 

    )
    fig_mapa.update_layout(
        mapbox=dict(center={"lat": df_filtrado["Latitud"].mean(), "lon": df_filtrado["Longitud"].mean()}, zoom=4.3),
        height=750,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # 📌 Gráfico de Línea del Cambio Porcentual Mensual
    df_long = df_filtrado.melt(id_vars=["Departamento"], value_vars=columnas_cambio, var_name="Mes", value_name="Cambio Porcentual")
    df_long["Mes"] = df_long["Mes"].str.replace("2025-", "Mes ")
    df_grouped = df_long.groupby("Mes")["Cambio Porcentual"].mean().reset_index()
    df_grouped["Mes"] = df_grouped["Mes"].apply(lambda x: convertir_mes(x))

    
    titulo_cp = ""
    if departamento and departamento != "Todos":
               if municipio and municipio != "Todos":
                   titulo_cp = f"Anomallia Porcentual promedio mensual en {municipio}, {departamento}"
               else:
                   titulo_cp = f"Anomalia Porcentual promedio mensual en  {departamento}"
    else:
               titulo_cp= "Anomalia Porcentual promedio mensual en Colombia "
    
    fig_line = px.line(
        df_grouped, x="Mes", y="Cambio Porcentual", markers=True, line_shape="spline",
        title=titulo_cp,
        labels={"Mes": "Mes", "Cambio Porcentual": "Porcentaje (%)"}

    )

    return fig_mapa, tarjeta_info_cambio, fig_line


# 🔥 Ejecutar app
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8050)


