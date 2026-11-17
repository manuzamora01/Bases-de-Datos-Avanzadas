import pandas as pd
import mysql.connector
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="unir_root",
    database="gasolineras_db"
)
cursor = conn.cursor()

df_maritimas = pd.read_excel('embarcacionesPrecios_es (1).xls', header=3)
cols_maritimas = ['Provincia', 'Municipio', 'Localidad', 'Código postal', 'Dirección', 'Longitud', 'Latitud', 'Rótulo', 'Horario', 'Precio gasolina 95 E5', 'Precio gasóleo A']
df_mar = df_maritimas[cols_maritimas].copy()
df_mar['tipo_estacion'] = 'Maritima'
df_mar['Margen'] = 'N/A'

df_terrestres_raw = pd.read_excel('preciosEESS_es (1).xls', header=3)
df_ter = df_terrestres_raw.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 9, 14, 35, 38]].copy()
df_ter.columns = ['Provincia', 'Municipio', 'Localidad', 'Código postal', 'Dirección', 'Margen', 'Longitud', 'Latitud', 'Precio gasolina 95 E5', 'Precio gasóleo A', 'Rótulo', 'Horario']
df_ter['tipo_estacion'] = 'Terrestre'

df_total = pd.concat([df_ter, df_mar], ignore_index=True)

df_total.fillna({'Rótulo': 'DESCONOCIDO', 'Localidad': 'DESCONOCIDA', 'Horario': 'No disponible', 'Margen': 'N/D', 'Dirección': 'No disponible', 'Código postal': '00000'}, inplace=True)
df_total['Latitud'] = df_total['Latitud'].astype(str).str.replace(',', '.')
df_total['Longitud'] = df_total['Longitud'].astype(str).str.replace(',', '.')

cache_provincias = {}
cache_municipios = {}
cache_localidades = {}
cache_empresas = {}
cache_combustibles = {}

cursor.execute("INSERT IGNORE INTO Combustible (id_combustible, tipo_combustible) VALUES (1, 'Gasolina 95 E5')")
cursor.execute("INSERT IGNORE INTO Combustible (id_combustible, tipo_combustible) VALUES (2, 'Gasóleo A')")
cache_combustibles['Precio gasolina 95 E5'] = 1
cache_combustibles['Precio gasóleo A'] = 2

id_prov_cnt = 1
id_mun_cnt = 1
id_loc_cnt = 1
id_est_cnt = 1
id_emp_cnt = 1

print("Iniciando ingesta de datos, esto puede tardar unos segundos...")

for index, row in df_total.iterrows():
    provincia = str(row['Provincia']).strip().upper()
    if provincia not in cache_provincias:
        cursor.execute("INSERT INTO Provincia (id_provincia, nombre_provincia) VALUES (%s, %s)", (id_prov_cnt, provincia))
        cache_provincias[provincia] = id_prov_cnt
        id_prov_cnt += 1
    id_prov_actual = cache_provincias[provincia]

    municipio = str(row['Municipio']).strip().upper()
    key_mun = f"{municipio}_{id_prov_actual}"
    if key_mun not in cache_municipios:
        cursor.execute("INSERT INTO Municipio (id_municipio, nombre_municipio, id_provincia) VALUES (%s, %s, %s)", (id_mun_cnt, municipio, id_prov_actual))
        cache_municipios[key_mun] = id_mun_cnt
        id_mun_cnt += 1
    id_mun_actual = cache_municipios[key_mun]

    localidad = str(row['Localidad']).strip().upper()
    key_loc = f"{localidad}_{id_mun_actual}"
    if key_loc not in cache_localidades:
        cursor.execute("INSERT INTO Localidad (id_localidad, nombre_localidad, id_municipio) VALUES (%s, %s, %s)", (id_loc_cnt, localidad, id_mun_actual))
        cache_localidades[key_loc] = id_loc_cnt
        id_loc_cnt += 1
    id_loc_actual = cache_localidades[key_loc]

    empresa = str(row['Rótulo']).strip().upper()
    if empresa not in cache_empresas:
        cursor.execute("INSERT INTO Empresa (id_empresa, nombre) VALUES (%s, %s)", (id_emp_cnt, empresa))
        cache_empresas[empresa] = id_emp_cnt
        id_emp_cnt += 1
    id_emp_actual = cache_empresas[empresa]

    try:
        lat = float(row['Latitud'])
        lon = float(row['Longitud'])
    except ValueError:
        lat, lon = 0.0, 0.0

    cp = str(row['Código postal']).replace('.0', '').strip().zfill(5)

    cursor.execute("""
        INSERT INTO Estacion (id_estacion, tipo_estacion, direccion, codigo_postal, latitud, longitud, margen, horario, id_localidad, id_empresa)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (id_est_cnt, row['tipo_estacion'], str(row['Dirección']).strip(), cp[:10], lat, lon, str(row['Margen']).strip()[:5], str(row['Horario']).strip(), id_loc_actual, id_emp_actual))

    precio_g95 = row['Precio gasolina 95 E5']
    if pd.notna(precio_g95):
        precio_val = float(str(precio_g95).replace(',', '.'))
        cursor.execute("INSERT INTO Precio_Historico (id_estacion, id_combustible, precio, fecha_actualizacion) VALUES (%s, %s, %s, %s)",
                       (id_est_cnt, cache_combustibles['Precio gasolina 95 E5'], precio_val, datetime.now().strftime("%Y-%m-%d")))

    precio_ga = row['Precio gasóleo A']
    if pd.notna(precio_ga):
        precio_val = float(str(precio_ga).replace(',', '.'))
        cursor.execute("INSERT INTO Precio_Historico (id_estacion, id_combustible, precio, fecha_actualizacion) VALUES (%s, %s, %s, %s)",
                       (id_est_cnt, cache_combustibles['Precio gasóleo A'], precio_val, datetime.now().strftime("%Y-%m-%d")))

    id_est_cnt += 1

conn.commit()
cursor.close()
conn.close()

print(f"Ingesta finalizada con éxito. Se han insertado {id_est_cnt - 1} estaciones.")