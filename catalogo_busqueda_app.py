import streamlit as st
import json
import unicodedata
import re
from pathlib import Path
import zipfile
import shutil
import os

# ==== CONFIGURACIÓN ====
JSON_PATH = "catalogo_ocr.json"
IMAGES_DIR = "thumbnails"
ZIP_PATH = "thumbnails.zip"
IMG_EXT = "jpg"
IMG_WIDTH = 800

# ==== DESCOMPRIMIR ZIP SI NO EXISTE LA CARPETA ====
if not Path(IMAGES_DIR).exists():
    if Path(ZIP_PATH).exists():
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall("temp_extract")  # Extraemos en carpeta temporal
        # Buscar imágenes en cualquier subcarpeta
        os.makedirs(IMAGES_DIR, exist_ok=True)
        for root, dirs, files in os.walk("temp_extract"):
            for file in files:
                if file.endswith(f".{IMG_EXT}"):
                    src = os.path.join(root, file)
                    dst = os.path.join(IMAGES_DIR, file)
                    shutil.move(src, dst)
        shutil.rmtree("temp_extract")  # Eliminamos carpeta temporal
        st.success("✅ Imágenes descomprimidas correctamente")
    else:
        st.warning("⚠ No se encontró el archivo thumbnails.zip para descomprimir")

# ==== FUNCIÓN PARA NORMALIZAR ====
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
st.title("📖 Catálogo DreamyScent")
st.write("Busca productos por nombre, descripción o palabra clave.")

# ==== CARGAR JSON ====
if not Path(JSON_PATH).exists():
    st.error(f"No se encuentra el archivo {JSON_PATH}. Súbelo al proyecto.")
    st.stop()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    catalogo = json.load(f)

# ==== BUSQUEDA ====
query = st.text_input("🔍 Escribe tu búsqueda:")
query_norm = normalizar_texto(query)

resultados = []
if query_norm:
    for pagina, texto in catalogo.items():
        texto_norm = normalizar_texto(texto)
        if query_norm in texto_norm:
            resultados.append((int(pagina), texto))

# ==== CONTROL DE IMAGEN ====
if "imagen_grande" not in st.session_state:
    st.session_state.imagen_grande = None

# ==== MOSTRAR RESULTADOS ====
st.write(f"Resultados encontrados: {len(resultados)}")

if resultados:
    for pagina, texto in sorted(resultados):
        img_path = f"{IMAGES_DIR}/page_{pagina}.{IMG_EXT}"
        fragmento = texto[:500] + "..." if len(texto) > 500 else texto
        if query:
            fragmento = re.sub(f"({query})", r"**\1**", fragmento, flags=re.IGNORECASE)

        st.markdown(f"### Página {pagina}")
        col1, col2 = st.columns([1, 2])
        with col1:
            if Path(img_path).exists():
                st.image(img_path, width=250)
                if st.button("🔍 Ver imagen completa", key=f"btn_{pagina}"):
                    st.session_state.imagen_grande = img_path
            else:
                st.warning("Imagen no encontrada")
        with col2:
            st.write(fragmento)
else:
    if query:
        st.warning("No se encontraron coincidencias.")

# ==== MOSTRAR IMAGEN GRANDE ====
if st.session_state.imagen_grande:
    st.write("---")
    st.subheader("Imagen completa")
    st.image(st.session_state.imagen_grande, width=IMG_WIDTH)
    if st.button("Cerrar imagen"):
        st.session_state.imagen_grande = None



