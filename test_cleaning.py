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

print("\n🏠 EJEMPLO DE TÍTULO CON FORMATO:")
print("Título original (con \\n):")
print(repr(df_raw['titulo'].iloc[0]))
print("\nTítulo formateado:")
print(df_raw['titulo'].iloc[0])

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

# 4. Extracción de características del título
print("\n🏠 4. EXTRAYENDO CARACTERÍSTICAS DEL TÍTULO...")

def extraer_caracteristicas(titulo):
    """
    Extrae metros cuadrados, ambientes, dormitorios, baños y cocheras del título
    Formato esperado: '102 m² tot.\n4 amb.\n2 dorm.\n2 baños'
    """
    if pd.isna(titulo):
        return None, None, None, None, None
    
    titulo_str = str(titulo)
    
    # Metros cuadrados (ej: "102 m² tot.")
    metros_match = re.search(r'(\d+)\s*m²', titulo_str)
    metros = int(metros_match.group(1)) if metros_match else None
    
    # Ambientes (ej: "4 amb.")
    amb_match = re.search(r'(\d+)\s*amb', titulo_str)
    ambientes = int(amb_match.group(1)) if amb_match else None
    
    # Dormitorios (ej: "2 dorm.")
    dorm_match = re.search(r'(\d+)\s*dorm', titulo_str)
    dormitorios = int(dorm_match.group(1)) if dorm_match else None
    
    # Baños (ej: "2 baños")
    bano_match = re.search(r'(\d+)\s*baño', titulo_str)
    banos = int(bano_match.group(1)) if bano_match else None
    
    # Cocheras (ej: "1 coch.")
    coch_match = re.search(r'(\d+)\s*coch', titulo_str)
    cocheras = int(coch_match.group(1)) if coch_match else 0
    
    return metros, ambientes, dormitorios, banos, cocheras

print("🔍 Extrayendo características del título...")
caracteristicas = df['titulo'].apply(extraer_caracteristicas)

# Crear columnas separadas
df['metros_cuadrados'] = [x[0] for x in caracteristicas]
df['ambientes'] = [x[1] for x in caracteristicas]
df['dormitorios'] = [x[2] for x in caracteristicas]
df['banos'] = [x[3] for x in caracteristicas]
df['cocheras'] = [x[4] for x in caracteristicas]

print("✅ Características extraídas correctamente!")

# Mostrar ejemplos de extracción
print("\n🔍 EJEMPLOS DE EXTRACCIÓN:")
ejemplo = df[['titulo', 'metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'cocheras']].head(5)
for idx, row in ejemplo.iterrows():
    print(f"\n{idx+1}. Título original:")
    # Mostrar título con saltos de línea reemplazados por | para mayor claridad
    titulo_visual = row['titulo'].replace('\n', ' | ')
    print(f"   {titulo_visual}")
    print(f"   📐 {row['metros_cuadrados']}m² | 🏠 {row['ambientes']} amb | 🛏️ {row['dormitorios']} dorm | 🚿 {row['banos']} baños | 🚗 {row['cocheras']} coch")

# Resumen de completitud
print("\n📊 COMPLETITUD DE EXTRACCIÓN:")
caracteristicas_cols = ['metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'cocheras']
for col in caracteristicas_cols:
    completitud = df[col].notna().sum()
    porcentaje = completitud / len(df) * 100
    print(f"{col}: {completitud}/{len(df)} ({porcentaje:.1f}%)")

# 5. Procesamiento de ubicaciones
print("\n📍 5. PROCESANDO UBICACIONES...")
df['barrio'] = df['ubicacion'].str.split(',').str[0].str.strip()
df['ciudad'] = df['ubicacion'].str.split(',').str[1].str.strip().fillna('Córdoba')

print("📍 UBICACIONES PROCESADAS:")
print(f"Barrios únicos: {df['barrio'].nunique()}")
print(f"Ciudades únicas: {df['ciudad'].nunique()}")

print("\n🏘️ TOP 5 BARRIOS MÁS FRECUENTES:")
print(df['barrio'].value_counts().head(5))

# 6. Variables derivadas
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

# 7. Guardar dataset limpio
print("\n💾 7. GUARDANDO DATASET LIMPIO...")
columnas_finales = [
    'titulo', 'precio_numerico', 'precio_por_m2', 'categoria_precio',
    'metros_cuadrados', 'categoria_tamano', 'ambientes', 'dormitorios', 
    'banos', 'cocheras', 'barrio', 'ciudad', 'descripcion'
]

# Filtrar datos válidos
df_final = df[columnas_finales].dropna(subset=['precio_numerico', 'metros_cuadrados'])

# Guardar dataset limpio
output_path = "data/zonaprop_clean.csv"
df_final.to_csv(output_path, index=False, encoding='utf-8')

print(f"✅ Dataset limpio guardado en: {output_path}")
print(f"📊 Propiedades guardadas: {len(df_final)}")
print(f"📋 Columnas guardadas: {len(df_final.columns)}")

# 8. Resumen final
print("\n🎉 ¡LIMPIEZA DE DATOS COMPLETADA!")
print("\n📊 RESUMEN ESTADÍSTICO:")
estadisticas = df_final[['precio_numerico', 'precio_por_m2', 'metros_cuadrados', 'ambientes', 'dormitorios']].describe()
print(estadisticas)

print("\n👀 VISTA PREVIA DEL DATASET LIMPIO:")
preview_cols = ['precio_numerico', 'metros_cuadrados', 'ambientes', 'dormitorios', 'banos', 'barrio']
print(df_final[preview_cols].head())

print("\n" + "=" * 60)
print("🎯 PROCESO COMPLETADO EXITOSAMENTE!")
print(f"📄 Dataset original: {len(df_raw)} propiedades")
print(f"📄 Dataset limpio: {len(df_final)} propiedades")
print(f"📊 Retención: {len(df_final)/len(df_raw)*100:.1f}%") 