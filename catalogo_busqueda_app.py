import streamlit as st
import json
import unicodedata
import re
from pathlib import Path
import zipfile
import os

# ==== CONFIGURACIÓN ====
JSON_PATH = "catalogo_ocr.json"   # OCR ya procesado
THUMBNAILS_ZIP = "thumbnails.zip" # Carpeta comprimida con miniaturas
IMAGES_ZIP = "imagenes.zip"       # Carpeta comprimida con imágenes grandes
THUMBNAILS_DIR = "thumbnails"
IMAGES_DIR = "imagenes"
IMG_EXT = "jpg"

# ==== DESCOMPRIMIR ZIP SI NO EXISTE LA CARPETA ====
def descomprimir_zip(zip_path, destino):
    if Path(zip_path).exists() and not Path(destino).exists():
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino)

descomprimir_zip(THUMBNAILS_ZIP, THUMBNAILS_DIR)
descomprimir_zip(IMAGES_ZIP, IMAGES_DIR)

# ==== FUNCIÓN PARA NORMALIZAR TEXTO ====
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

# ==== INTERFAZ ====
st.set_page_config(page_title="Catálogo DreamyScent", layout="wide")
st.title("📖 Catálogo DreamyScent")
st.write("Busca productos por **nombre**, **descripción** o **palabra clave**.")

# ==== CARGAR JSON ====
if not Path(JSON_PATH).exists():
    st.error(f"No se encuentra el archivo {JSON_PATH}. Súbelo al proyecto.")
    st.stop()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    catalogo = json.load(f)

# ==== INPUT BUSQUEDA ====
query = st.text_input("🔍 Escribe tu búsqueda:")
query_norm = normalizar_texto(query)

resultados = []
if query_norm:
    for pagina, texto in catalogo.items():
        texto_norm = normalizar_texto(texto)
        if query_norm in texto_norm:
            resultados.append((int(pagina), texto))

# ==== RESULTADOS ====
st.write(f"Resultados encontrados: {len(resultados)}")

if resultados:
    # Columnas dinámicas (para móviles: 1 columna, escritorio: 3 columnas)
    columnas = st.columns(1 if st.session_state.get('is_mobile', False) else 3)
    for idx, (pagina, texto) in enumerate(sorted(resultados)):
        img_path = f"{THUMBNAILS_DIR}/page_{pagina}.{IMG_EXT}"
        full_img_path = f"{IMAGES_DIR}/page_{pagina}.{IMG_EXT}"

        # Fragmento con resaltado
        fragmento = texto[:300] + "..." if len(texto) > 300 else texto
        if query:
            fragmento = re.sub(f"({query})", r"**\1**", fragmento, flags=re.IGNORECASE)

        with columnas[idx % len(columnas)]:
            st.markdown(f"### Página {pagina}")
            if Path(img_path).exists():
                if st.button(f"Ver página {pagina}", key=f"btn_{pagina}"):
                    st.session_state['img_modal'] = full_img_path
                st.image(img_path, width="stretch")
            else:
                st.warning("Imagen no encontrada")
            st.caption(fragmento)

# ==== MODAL PARA IMAGEN COMPLETA ====
if 'img_modal' in st.session_state:
    st.write("---")
    st.image(st.session_state['img_modal'], width=700)
    if st.button("Cerrar imagen"):
        del st.session_state['img_modal']
else:
    st.write("---")

