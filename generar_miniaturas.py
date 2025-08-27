import fitz  # PyMuPDF
import os
from PIL import Image

# Archivo PDF
PDF_PATH = "catalogo DREAMYSCENT.pdf"
# Carpeta donde se guardarán las miniaturas
THUMBNAIL_DIR = "thumbnails"
# Ancho de la miniatura en píxeles
THUMB_WIDTH = 500

# Crear carpeta si no existe
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# Abrir PDF
doc = fitz.open(PDF_PATH)
total_pages = doc.page_count

print(f"Generando miniaturas para {total_pages} páginas...")

for page_num in range(total_pages):
    page = doc.load_page(page_num)
    pix = page.get_pixmap(dpi=150)  # render base
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Redimensionar manteniendo proporción
    ratio = THUMB_WIDTH / img.width
    new_height = int(img.height * ratio)
    img = img.resize((THUMB_WIDTH, new_height), Image.Resampling.LANCZOS)

    # Guardar miniatura
    img_path = os.path.join(THUMBNAIL_DIR, f"page_{page_num}.jpg")
    img.save(img_path, "JPEG", quality=80)

    print(f"✅ Miniatura creada: {img_path}")

print(f"\n🎉 Miniaturas generadas en la carpeta: {THUMBNAIL_DIR}")