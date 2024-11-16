import streamlit as st
import requests
import pandas as pd
import psycopg2

# Datos de conexiÃ³n a la base de datos PostgreSQL
dbname = "empresa_db"  # Nombre de la base de datos que creaste en pgAdmin
user = "postgres"
password = "Colombia18$"
host = "localhost"
port = "5433"

# URL de la API
url = "https://www.datos.gov.co/resource/qmzu-gj57.json"

# Obtener datos de la API
try:
    response = requests.get(url)
    response.raise_for_status()  # Verificar si la peticiÃ³n fue exitosa
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"Error al obtener datos: {e}")
    data = []  # Si hay error, data estarÃ¡ vacÃ­a

# Si hay datos, se convierten en DataFrame y se muestran en Streamlit
if data:
    df = pd.DataFrame(data)
    st.write("## Empresas")
    st.dataframe(df)  # Mostrar la tabla en Streamlit

    # Conectar a la base de datos PostgreSQL usando parÃ¡metros directamente
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cursor = conn.cursor()

        # Insertar cada fila del DataFrame en la tabla hack_empresa
        for index, row in df.iterrows():
            # Convertir todos los valores de la fila a cadenas de texto
            values = {col: str(row.get(col, "")) for col in df.columns}
            
            # Generar la consulta INSERT en un string
            insert_query = cursor.mogrify(
                """
                INSERT INTO hack_empresa (
                    codigo, nombre, nit, es_entidad, es_grupo, esta_activa,
                    fecha_creacion, codigo_categoria_principal, descripcion_categoria_principal,
                    telefono, fax, correo, direccion, pais, departamento, municipio,
                    sitio_web, tipo_empresa, nombre_representante_legal,
                    tipo_doc_representante_legal, n_mero_doc_representante_legal,
                    telefono_representante_legal, correo_representante_legal,
                    espyme, ubicacion
                ) VALUES (
                    %(codigo)s, %(nombre)s, %(nit)s, %(es_entidad)s, %(es_grupo)s, %(esta_activa)s,
                    %(fecha_creacion)s, %(codigo_categoria_principal)s, %(descripcion_categoria_principal)s,
                    %(telefono)s, %(fax)s, %(correo)s, %(direccion)s, %(pais)s, %(departamento)s, %(municipio)s,
                    %(sitio_web)s, %(tipo_empresa)s, %(nombre_representante_legal)s,
                    %(tipo_doc_representante_legal)s, %(n_mero_doc_representante_legal)s,
                    %(telefono_representante_legal)s, %(correo_representante_legal)s,
                    %(espyme)s, %(ubicacion)s
                )
                """,
                values
            )

            # Mostrar la consulta en Streamlit
            st.write(f"**Sentencia INSERT para la fila {index + 1}:**")
            st.code(insert_query.decode("utf-8"))  # Mostrar la consulta en pantalla como texto
            
            # Ejecutar la consulta
            cursor.execute(insert_query)

        # Confirmar los cambios en la base de datos
        conn.commit()
        st.success("Datos insertados en la base de datos exitosamente.")
    
    except psycopg2.Error as e:
        st.error(f"Error al conectar o insertar en PostgreSQL: {e}")
    
    finally:
        # Cerrar la conexiÃ³n si existe
        if conn is not None:
            cursor.close()
            conn.close()
else:
    st.write("No se encontraron datos.")
