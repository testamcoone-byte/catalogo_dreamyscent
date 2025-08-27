import streamlit as st
import json
import unicodedata
import re
from pathlib import Path
import zipfile
import base64

# ==== CONFIGURACIÓN ====
JSON_PATH = "catalogo_ocr.json"
IMAGES_DIR = "thumbnails"
ZIP_FILE = "thumbnails.zip"
IMG_EXT = "jpg"
IMG_WIDTH = 800
LOGO_PATH = "perfumes.jpg"  # Imagen del logo

# ==== ESTILOS ====
st.markdown("""
    <style>
    body {
        background-color: #1a1a1a;
        color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .logo-container img {
        width: 180px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .titulo {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #f8d210;
        margin-bottom: 5px;
    }
    .subtitulo {
        text-align: center;
        font-size: 16px;
        color: #f5f5f5;
        margin-bottom: 20px;
    }
    .result-card {
        background: #2a2a2a;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==== FUNCIONES ====
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    # Quitar caracteres raros y ordenar
    texto = re.sub(r'[_\|\-\—"“”]+', ' ', texto)
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto).strip()
    # Insertar saltos de línea en secciones clave
    texto = re.sub(r'(Notas de Salida|Notas de Corazón|Notas de Fondo|Genero|Cantidad|Clima)',
                   r'\n\1', texto, flags=re.IGNORECASE)
    # Negritas en etiquetas
    texto = re.sub(r'(Notas de Salida|Notas de Corazón|Notas de Fondo|Genero|Cantidad|Clima)',
                   r'**\1**', texto, flags=re.IGNORECASE)
    # Formatear por líneas
    lineas = [linea.strip().capitalize() for linea in texto.split("\n") if linea.strip()]
    return "\n".join(lineas)

def cargar_logo(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

# ==== DESCOMPRIMIR SI ES NECESARIO ====
if not Path(IMAGES_DIR).exists():
    if Path(ZIP_FILE).exists():
        st.info("Descomprimiendo imágenes...")
        with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
            zip_ref.extractall(IMAGES_DIR)
        st.success("Imágenes descomprimidas.")
    else:
        st.warning(f"No se encuentra la carpeta '{IMAGES_DIR}' ni el ZIP '{ZIP_FILE}'.")

# ==== CABECERA ====
logo_base64 = cargar_logo(LOGO_PATH)
if logo_base64:
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo"/>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Logo no encontrado.")

st.markdown('<div class="titulo">📖 Catálogo DreamyScent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Busca productos por nombre, descripción o palabra clave</div>', unsafe_allow_html=True)

# ==== CARGAR JSON ====
if not Path(JSON_PATH).exists():
    st.error(f"No se encuentra el archivo {JSON_PATH}. Súbelo al proyecto.")
    st.stop()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    catalogo = json.load(f)

# ==== BARRA DE BÚSQUEDA ====
query = st.text_input("🔍 Escribe tu búsqueda:")
col1, col2 = st.columns([1, 1])
with col1:
    buscar = st.button("Buscar 🔍")

resultados = []
query_norm = normalizar_texto(query)

if buscar and query_norm:
    for pagina, data in catalogo.items():
        texto = data if isinstance(data, str) else data.get("texto", "")
        texto_norm = normalizar_texto(texto)
        if query_norm in texto_norm:
            resultados.append((int(pagina), texto))

if buscar:
    st.write(f"Resultados encontrados: {len(resultados)}")

# ==== MOSTRAR RESULTADOS ====
if resultados:
    for pagina, texto in sorted(resultados):
        img_path = f"{IMAGES_DIR}/page_{pagina}.{IMG_EXT}"
        texto_limpio = limpiar_texto(texto)

        with st.container():
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### Página {pagina}")
            col1, col2 = st.columns([1, 2])
            with col1:
                if Path(img_path).exists():
                    st.image(img_path, width=300)
                else:
                    st.warning("Imagen no encontrada")
            with col2:
                st.write(texto_limpio)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    if buscar and query:
        st.warning("No se encontraron coincidencias.")
