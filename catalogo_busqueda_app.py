import streamlit as st
import json
import unicodedata
import re
from pathlib import Path
import zipfile

# ==== CONFIGURACIÓN ====
JSON_PATH = "catalogo_ocr.json"
IMAGES_DIR = "thumbnails"
ZIP_FILE = "thumbnails.zip"  # Subir este ZIP en la nube si no hay carpeta
IMG_EXT = "jpg"
IMG_WIDTH = 1000  # Imagen completa más grande para mejor calidad

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
    """Elimina caracteres raros y formatea campos clave"""
    if not isinstance(texto, str):
        return ""
    # Quitar caracteres innecesarios
    texto = re.sub(r'[\|\-\—]+', ' ', texto)
    texto = re.sub(r'\(l', '', texto, flags=re.IGNORECASE)
    # Unir líneas y quitar espacios duplicados
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    # Negrita para campos comunes
    texto = re.sub(r'(Genero|Cantidad|Clima)', r'**\1**', texto, flags=re.IGNORECASE)
    return texto

# ==== DESCOMPRIMIR SI ES NECESARIO ====
if not Path(IMAGES_DIR).exists():
    if Path(ZIP_FILE).exists():
        st.info("Descomprimiendo imágenes...")
        with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
            zip_ref.extractall(IMAGES_DIR)
        st.success("Imágenes descomprimidas.")
    else:
        st.warning(f"No se encuentra la carpeta '{IMAGES_DIR}' ni el ZIP '{ZIP_FILE}'.")

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
    for pagina, data in catalogo.items():
        texto = data if isinstance(data, str) else data.get("texto", "")
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

        # Limpiar y preparar fragmento
        texto_limpio = limpiar_texto(texto)
        fragmento = texto_limpio[:500] + "..." if len(texto_limpio) > 500 else texto_limpio
        if query:
            fragmento = re.sub(f"({query})", r"**\1**", fragmento, flags=re.IGNORECASE)

        # Mostrar resultados
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
