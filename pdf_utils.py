import fitz  # PyMuPDF
import base64
import os
import io
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_pdf_data(filepath: str) -> dict:
    doc = fitz.open(filepath)
    pages = []

    for i, page in enumerate(doc):
        # 1. Native text extraction
        native_text = page.get_text().strip()

        # 2. OCR text extraction
        ocr_image = render_page_as_image(page)
        ocr_text = pytesseract.image_to_string(ocr_image).strip()

        # 3. Combine or compare (customize as needed)
        combined_text = merge_text(native_text, ocr_text)

        # 4. Extract embedded images
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_format = base_image["ext"]
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            images.append({"format": image_format, "data": encoded_image})

        pages.append({
            "page_number": i + 1,
            "text": combined_text,
            "native_text": native_text,
            "ocr_text": ocr_text,
            "images": images,
        })

    doc.close()
    return {
        "filename": os.path.basename(filepath),
        "pages": pages,
    }

def merge_text(native_text: str, ocr_text: str) -> str:
    # Avoid duplication if texts are very similar
    if ocr_text.strip() in native_text:
        return native_text
    if native_text.strip() in ocr_text:
        return ocr_text

    # Otherwise, concatenate both
    return f"{native_text}\n\n[OCR Supplement]\n{ocr_text}"

def render_page_as_image(page, zoom=2):
    mat = fitz.Matrix(zoom, zoom)  # zoom > 1 for higher resolution
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))
