import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

print("🧹 INICIANDO LIMPIEZA DE DATOS - ZONAPROP SCRAPER")
print("=" * 60)

# 1. Cargar datos raw
print("\n📁 1. CARGANDO DATOS RAW...")
df_raw = pd.read_csv("data/zonaprop_raw.csv")

print(f"📊 Dataset cargado: {len(df_raw)} propiedades")
print(f"📋 Columnas: {list(df_raw.columns)}")
print(f"💾 Tamaño: {df_raw.shape}")

# 2. Exploración inicial
print("\n🔍 2. EXPLORACIÓN INICIAL...")
print("📏 TIPOS DE DATOS:")
print(df_raw.dtypes)

# Mostrar algunos ejemplos del campo titulo para ver la estructura
print("\n📝 Ejemplos del campo titulo (ahora direcciones):")
print(repr(df_raw['titulo'].iloc[0]))
print("Visualización normal:")
print(df_raw['titulo'].iloc[0])

# Verificar si tenemos el campo caracteristicas
if 'caracteristicas' in df_raw.columns:
    print("\n📝 Ejemplos del campo caracteristicas:")
    print(repr(df_raw['caracteristicas'].iloc[0]))
    print("Visualización normal:")
    print(df_raw['caracteristicas'].iloc[0])
else:
    print("⚠️ Campo 'caracteristicas' no encontrado en los datos")

# Comprobar si hay saltos de línea en los datos de características
if 'caracteristicas' in df_raw.columns:
    print("\n🔍 Verificando saltos de línea en características:")
    ejemplos_con_saltos = df_raw['caracteristicas'].str.contains('\n', na=False)
    print(f"Registros con saltos de línea: {ejemplos_con_saltos.sum()}")
    
    if ejemplos_con_saltos.any():
        print("Ejemplo con salto de línea:")
        ejemplo = df_raw[ejemplos_con_saltos]['caracteristicas'].iloc[0]
        print(f"Raw: {repr(ejemplo)}")
        print(f"Clean: {ejemplo}")

# Función para limpiar los datos de características
def limpiar_caracteristicas(caracteristicas):
    if pd.isna(caracteristicas):
        return ""
    # Reemplazar saltos de línea con espacios y limpiar espacios extra
    return ' '.join(str(caracteristicas).split())

# Aplicar limpieza a las características si el campo existe
if 'caracteristicas' in df_raw.columns:
    df_raw['caracteristicas'] = df_raw['caracteristicas'].apply(limpiar_caracteristicas)

# Funciones auxiliares para extraer características específicas
def extraer_metros(caracteristicas):
    if pd.isna(caracteristicas):
        return None
    metros_match = re.search(r'(\d+)\s*m²', str(caracteristicas))
    return int(metros_match.group(1)) if metros_match else None

def extraer_ambientes(caracteristicas):
    if pd.isna(caracteristicas):
        return None
    amb_match = re.search(r'(\d+)\s*amb', str(caracteristicas))
    return int(amb_match.group(1)) if amb_match else None

def extraer_dormitorios(caracteristicas):
    if pd.isna(caracteristicas):
        return None
    dorm_match = re.search(r'(\d+)\s*dorm', str(caracteristicas))
    return int(dorm_match.group(1)) if dorm_match else None

def extraer_banos(caracteristicas):
    if pd.isna(caracteristicas):
        return None
    bano_match = re.search(r'(\d+)\s*baño', str(caracteristicas))
    return int(bano_match.group(1)) if bano_match else None

def extraer_cocheras(caracteristicas):
    if pd.isna(caracteristicas):
        return None
    coch_match = re.search(r'(\d+)\s*coch', str(caracteristicas))
    return int(coch_match.group(1)) if coch_match else None

# Aplicar extracción de características si el campo existe
if 'caracteristicas' in df_raw.columns:
    print("🔍 Extrayendo características del campo 'caracteristicas'...")
    
    # Aplicar cada función por separado
    df_raw['metros_cuadrados'] = df_raw['caracteristicas'].apply(extraer_metros)
    df_raw['ambientes'] = df_raw['caracteristicas'].apply(extraer_ambientes)
    df_raw['dormitorios'] = df_raw['caracteristicas'].apply(extraer_dormitorios)
    df_raw['banos'] = df_raw['caracteristicas'].apply(extraer_banos)
    df_raw['cocheras'] = df_raw['caracteristicas'].apply(extraer_cocheras)
    
    # Asignar df_raw como df
    df = df_raw.copy()
else:
    print("⚠️ No se puede extraer características: campo 'caracteristicas' no encontrado")
    # Crear columnas vacías
    df_raw['metros_cuadrados'] = None
    df_raw['ambientes'] = None
    df_raw['dormitorios'] = None
    df_raw['banos'] = None
    df_raw['cocheras'] = None
    df = df_raw.copy()

# Mostrar ejemplos de extracción
print("\n📊 Ejemplos de extracción de características:")
if 'caracteristicas' in df_raw.columns:
    ejemplo = df[['titulo', 'caracteristicas', 'metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'cocheras']].head(5)
else:
    ejemplo = df[['titulo', 'metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'cocheras']].head(5)

for i, row in ejemplo.iterrows():
    print(f"\n📍 Dirección: {row['titulo']}")
    if 'caracteristicas' in df_raw.columns:
        caracteristicas_visual = row['caracteristicas'].replace('\n', ' | ')
        print(f"   📋 Características: {caracteristicas_visual}")
    print(f"   📏 Metros: {row['metros_cuadrados']}")
    print(f"   🏠 Ambientes: {row['ambientes']}")
    print(f"   🛏️  Dormitorios: {row['dormitorios']}")
    print(f"   🚿 Baños: {row['banos']}")
    print(f"   🚗 Cocheras: {row['cocheras']}")

# 3. Limpieza de precios
print("\n💰 3. LIMPIANDO PRECIOS...")
df = df_raw.copy()

def limpiar_precio(precio_str):
    """
    Convierte string de precio a número
    Ej: '$ 650.000' -> 650000
    """
    if pd.isna(precio_str) or precio_str == "Sin precio":
        return None
    
    # Remover $ y espacios, convertir puntos a nada
    precio_limpio = re.sub(r'[^\d]', '', str(precio_str))
    
    try:
        return int(precio_limpio)
    except:
        return None

df['precio_numerico'] = df['precio'].apply(limpiar_precio)

print("🧹 ANTES vs DESPUÉS - PRECIOS:")
comparacion_precios = df[['precio', 'precio_numerico']].head(5)
print(comparacion_precios)

# 4. Variables derivadas
print("\n💡 6. CREANDO VARIABLES DERIVADAS...")
df['precio_por_m2'] = df['precio_numerico'] / df['metros_cuadrados']

def categorizar_precio(precio):
    if pd.isna(precio):
        return "Sin datos"
    elif precio < 500000:
        return "Económico"
    elif precio < 800000:
        return "Medio"
    elif precio < 1200000:
        return "Alto"
    else:
        return "Premium"

df['categoria_precio'] = df['precio_numerico'].apply(categorizar_precio)

def categorizar_tamano(metros):
    if pd.isna(metros):
        return "Sin datos"
    elif metros < 50:
        return "Pequeño"
    elif metros < 80:
        return "Mediano"
    elif metros < 120:
        return "Grande"
    else:
        return "Muy grande"

df['categoria_tamano'] = df['metros_cuadrados'].apply(categorizar_tamano)

print("💡 VARIABLES DERIVADAS CREADAS:")
print(f"✅ precio_por_m2: Promedio ${df['precio_por_m2'].mean():.0f}/m²")
print(f"✅ categoria_precio: {df['categoria_precio'].value_counts().to_dict()}")
print(f"✅ categoria_tamano: {df['categoria_tamano'].value_counts().to_dict()}")

# 5. Procesamiento de ubicaciones
print("\n📍 5. PROCESANDO UBICACIONES...")
df['barrio'] = df['ubicacion'].str.split(',').str[0].str.strip()
df['ciudad'] = df['ubicacion'].str.split(',').str[1].str.strip().fillna('Córdoba')

print("📍 UBICACIONES PROCESADAS:")
print(f"Barrios únicos: {df['barrio'].nunique()}")
print(f"Ciudades únicas: {df['ciudad'].nunique()}")

print("\n🏘️ TOP 5 BARRIOS MÁS FRECUENTES:")
print(df['barrio'].value_counts().head(5))

# 6. Guardar dataset limpio
print("\n💾 7. GUARDANDO DATASET LIMPIO...")
columns_order = [
    'titulo', 'caracteristicas', 'precio_numerico', 'precio_por_m2', 'categoria_precio',
    'metros_cuadrados', 'categoria_tamano', 'ambientes', 'dormitorios', 
    'banos', 'cocheras', 'barrio', 'ciudad', 'descripcion'
]

# Filtrar solo las columnas que existen en el DataFrame
existing_columns = [col for col in columns_order if col in df.columns]
df_clean = df[existing_columns]

# Guardar dataset limpio
output_path = "data/zonaprop_clean.csv"
df_clean.to_csv(output_path, index=False, encoding='utf-8')

print(f"✅ Dataset limpio guardado en: {output_path}")
print(f"📊 Propiedades guardadas: {len(df_clean)}")
print(f"📋 Columnas guardadas: {len(df_clean.columns)}")

# 8. Resumen final
print("\n🎉 ¡LIMPIEZA DE DATOS COMPLETADA!")
print("\n📊 RESUMEN ESTADÍSTICO:")
estadisticas = df_clean[['precio_numerico', 'precio_por_m2', 'metros_cuadrados', 'ambientes', 'dormitorios']].describe()
print(estadisticas)

print("\n👀 VISTA PREVIA DEL DATASET LIMPIO:")
preview_cols = ['precio_numerico', 'metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'barrio']
print(df_clean[preview_cols].head())

print("\n" + "=" * 60)
print("🎯 PROCESO COMPLETADO EXITOSAMENTE!")
print(f"📄 Dataset original: {len(df_raw)} propiedades")
print(f"📄 Dataset limpio: {len(df_clean)} propiedades")
print(f"📊 Retención: {len(df_clean)/len(df_raw)*100:.1f}%") 