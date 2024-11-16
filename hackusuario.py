import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

# ConfiguraciÃ³n de la pÃ¡gina
st.set_page_config(page_title="Supply Sense - B&uacute;squeda Avanzada", page_icon=":office:", layout="wide")

# ParÃ¡metros de conexiÃ³n a la base de datos PostgreSQL
db_params = {
    "dbname": "empresa_db",
    "user": "postgres",
    "password": "Colombia18$",
    "host": "localhost",
    "port": "5433"
}

# CSS personalizado
st.markdown("""
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #0078D4;
            text-align: center;
            margin-bottom: 20px;
        }
        .container {
            background-color: #F3F2F1;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .highlight {
            font-size: 18px;
            font-weight: bold;
            color: #FF5722;
        }
    </style>
""", unsafe_allow_html=True)

# FunciÃ³n para autenticaciÃ³n simulada
def authenticate(username, password):
    return username == "cliente" and password == "123123"

# FunciÃ³n para conectarse a la base de datos
def connect_to_db():
    try:
        return psycopg2.connect(**db_params)
    except psycopg2.Error as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# FunciÃ³n para ejecutar consultas y devolver un DataFrame
def fetch_data(query, params=None):
    conn = connect_to_db()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error al ejecutar la consulta: {e}")
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

# TÃ­tulo de la aplicaciÃ³n
st.markdown('<div class="main-title">Supply Sense - B&uacute;squeda Avanzada</div>', unsafe_allow_html=True)
st.image("D:/Mauricio/BootCamp/Hackhaton/image-removebg-preview (3).png", width=150)

# Estado de autenticaciÃ³n
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("Iniciar Sesi&oacute;n")
    username = st.text_input("Usuario")
    password = st.text_input("Contrase&ntilde;a", type="password")
    if st.button("Iniciar sesi&oacute;n"):
        if authenticate(username, password):
            st.success("Autenticaci&oacute;n exitosa.")
            st.session_state.authenticated = True
        else:
            st.error("Usuario o contrase&ntilde;a incorrectos.")
else:
    # MenÃº de navegaciÃ³n
    st.sidebar.title("Men&uacute;")
    st.sidebar.write("B&uacute;squeda Avanzada")

    # Contenedor principal
    with st.container():
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.header("B&uacute;squeda Avanzada de Proveedores")

        # Filtro de departamentos y municipios
        query_departamentos = "SELECT DISTINCT departamento FROM hack_empresa ORDER BY departamento"
        df_departamentos = fetch_data(query_departamentos)
        departamentos = ["Todas"] + df_departamentos["departamento"].dropna().tolist()
        departamento = st.selectbox("Departamento", departamentos)
        
        if departamento != "Todas":
            query_municipios = "SELECT DISTINCT municipio FROM hack_empresa WHERE departamento = %s ORDER BY municipio"
            df_municipios = fetch_data(query_municipios, params=(departamento,))
        else:
            query_municipios = "SELECT DISTINCT municipio FROM hack_empresa ORDER BY municipio"
            df_municipios = fetch_data(query_municipios)

        municipios = ["Todas"] + df_municipios["municipio"].dropna().tolist()
        municipio = st.selectbox("Municipio", municipios)
        
        query_industria = "SELECT DISTINCT descripcion_categoria_principal FROM hack_empresa ORDER BY descripcion_categoria_principal"
        df_industria= fetch_data(query_industria)
        industrias=df_industria["descripcion_categoria_principal"].dropna().tolist()
        industria= st.selectbox("Industria", industrias)

        # Filtros adicionales
        rango_historial = st.slider("Historial Proyectos", 0, 100, (0, 100))
        rango_alertas = st.slider("Alertas Incumplimiento", 0, 100, (0, 100))
        rango_certificaciones = st.slider("Certificaciones Normativo", 0, 100, (0, 100))
        rango_aceptabilidad = st.slider("Puntaje Aceptabilidad", 0, 100, (0, 100))
        rango_confiabilidad = st.slider("Puntaje Confiabilidad", 0, 100, (0, 100))
        rango_logistica = st.slider("Puntaje Log&iacute;stica y Entrega", 0, 100, (0, 100))
        rango_negociacion = st.slider("Puntaje Capacidad Negociaci&oacute;n", 0, 100, (0, 100))
        rango_comunicacion = st.slider("Puntaje Comunicaci&oacute;n y Coordinaci&oacute;n", 0, 100, (0, 100))

        # Filtro destacado: Indicador Unificado
        st.markdown('<div class="highlight">Indicador Unificado</div>', unsafe_allow_html=True)
        rango_unificado = st.slider("Indicador Unificado", 0, 100, (0, 100))

       

        # ConstrucciÃ³n de consulta SQL
        consulta_sql = "SELECT * FROM hack_empresa"
        condiciones = []
        parametros = []

        if departamento != "Todas":
            condiciones.append("departamento = %s")
            parametros.append(departamento)

        if municipio != "Todas":
            condiciones.append("municipio = %s")
            parametros.append(municipio)
            
        if industria !='Otro':
            condiciones.append("descripcion_categoria_principal = %s")
            parametros.append(industria)

        for campo, rango, default_rango in [
            ("historial_proyectos", rango_historial, (0, 100)),
            ("alertas_incumplimiento", rango_alertas, (0, 100)),
            ("certificaciones_normativo", rango_certificaciones, (0, 100)),
            ("puntaje_aceptabilidad", rango_aceptabilidad, (0, 100)),
            ("puntaje_confiabilidad", rango_confiabilidad, (0, 100)),
            ("puntaje_logistica_entrega", rango_logistica, (0, 100)),
            ("puntaje_capacidad_negociacion", rango_negociacion, (0, 100)),
            ("puntaje_comunicacion_coord", rango_comunicacion, (0, 100)),
            ("indicador_unificado", rango_unificado, (0, 100)),
        ]:
            if rango != default_rango:
                condiciones.append(f"{campo} BETWEEN %s AND %s")
                parametros.extend(rango)

        if condiciones:
            consulta_sql += " WHERE " + " AND ".join(condiciones)

        st.write("Consulta SQL generada:")
        st.code(consulta_sql)
        st.write("ParÃ¡metros:", parametros)

        # BotÃ³n para buscar
        if st.button("Buscar Empresas"):
            df_resultado = fetch_data(consulta_sql, parametros)

            if not df_resultado.empty:
                st.write("### Resultados de la b&uacute;squeda")
                st.dataframe(df_resultado)

                # GrÃ¡fica de pastel
                total_empresas = 1000
                porcentaje = (len(df_resultado) / total_empresas) * 100
                fig, ax = plt.subplots()
                ax.pie([porcentaje, 100 - porcentaje], labels=["Resultado", "Restante"], autopct="%1.1f%%")
                ax.set_title("Resultados")
                st.pyplot(fig)
            else:
                st.warning("No se encontraron resultados.")