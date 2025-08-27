import streamlit as st
import json
import unicodedata
import re
from pathlib import Path
import zipfile
import os

# ==== CONFIGURACIÓN ====
JSON_PATH = "catalogo_ocr.json"  # OCR procesado
IMG_DIR = "thumbnails"           # Carpeta para miniaturas
IMG_EXT = "jpg"                  # Extensión imágenes
IMG_FULL_DIR = "imagenes"        # Carpeta imágenes grandes

# ==== 1. DESCOMPRIMIR ZIP AUTOMÁTICAMENTE ====
def descomprimir_zip(archivo_zip, carpeta_destino):
    if os.path.exists(archivo_zip) and not os.path.exists(carpeta_destino):
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        print(f"✅ {archivo_zip} descomprimido en {carpeta_destino}")
    else:
        print(f"✔ {carpeta_destino} ya existe o no se encontró {archivo_zip}")

descomprimir_zip("imagenes.zip", IMG_FULL_DIR)
descomprimir_zip("thumbnails.zip", IMG_DIR)

# ==== 2. NORMALIZAR TEXTO ====
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

# ==== 3. INTERFAZ ====
st.set_page_config(page_title="Catálogo DreamyScent", layout="wide")
st.title("📖 Catálogo DreamyScent")
st.write("Busca productos por nombre, descripción o palabra clave.")

# ==== 4. CARGAR DATOS ====
if not Path(JSON_PATH).exists():
    st.error(f"No se encuentra el archivo {JSON_PATH}. Sube el archivo al repositorio.")
    st.stop()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    catalogo = json.load(f)

# ==== 5. BUSQUEDA ====
query = st.text_input("🔍 Escribe tu búsqueda:")
query_norm = normalizar_texto(query)

resultados = []
if query_norm:
    for pagina, texto in catalogo.items():
        texto_norm = normalizar_texto(texto)
        if query_norm in texto_norm:
            resultados.append((int(pagina), texto))

st.write(f"Resultados encontrados: {len(resultados)}")

# ==== 6. MOSTRAR RESULTADOS ====
if resultados:
    for pagina, texto in sorted(resultados):
        img_path = f"{IMG_DIR}/page_{pagina}.{IMG_EXT}"
        img_full_path = f"{IMG_FULL_DIR}/page_{pagina}.{IMG_EXT}"

        # Fragmento con búsqueda resaltada
        fragmento = texto[:400] + "..." if len(texto) > 400 else texto
        if query:
            fragmento = re.sub(f"({query})", r"**\1**", fragmento, flags=re.IGNORECASE)

        # Layout
        col1, col2 = st.columns([1, 2])
        with col1:
            if Path(img_path).exists():
                # Miniatura
                if st.button(f"🔍 Ver página {pagina}", key=f"btn_{pagina}"):
                    st.session_state["imagen_completa"] = img_full_path
                st.image(img_path, width=150)
            else:
                st.warning("Imagen no encontrada")

        with col2:
            st.markdown(f"### Página {pagina}")
            st.write(fragmento)

    # ==== POPUP DE IMAGEN COMPLETA ====
    if "imagen_completa" in st.session_state:
        st.write("### 🖼 Imagen completa")
        if Path(st.session_state["imagen_completa"]).exists():
            st.image(st.session_state["imagen_completa"], use_container_width=True)
            if st.button("❌ Cerrar"):
                del st.session_state["imagen_completa"]
else:
    if query:
        st.warning("No se encontraron coincidencias.")
