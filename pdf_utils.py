import fitz  # PyMuPDF
import base64
import os
import io
import pytesseract
from PIL import Image

def extract_pdf_data(filepath: str) -> dict:
    doc = fitz.open(filepath)
    pages = []

    for i, page in enumerate(doc):
        # 1. Native text extraction
        native_text = page.get_text().strip()

        # 2. Render page as image for OCR
        ocr_image = render_page_as_image(page)
        
        # 3. OCR full text
        ocr_text = pytesseract.image_to_string(ocr_image).strip()

        # 4. Table detection via OCR layout
        layout_data = pytesseract.image_to_data(ocr_image, output_type=pytesseract.Output.DICT)
        table_text_blocks = extract_table_blocks(layout_data)

        # 5. Extract embedded images and nearby figure captions
        images = []
        figure_captions = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_format = base_image["ext"]
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            images.append({"format": image_format, "data": encoded_image})

            # Rough approximation of figure captions: text below image bbox
            img_rect = fitz.Rect(img[1], img[2], img[3], img[4])  # get image rectangle
            caption_candidates = page.get_text("blocks")
            for block in caption_candidates:
                b_x0, b_y0, b_x1, b_y1, text = block[:5]
                if text.strip().lower().startswith("figure") and b_y0 > img_rect.y1:
                    figure_captions.append(text.strip())
                    break

        # 6. Combine text
        combined_text = merge_text(native_text, ocr_text)

        pages.append({
            "page_number": i + 1,
            "text": combined_text,
            "native_text": native_text,
            "ocr_text": ocr_text,
            "tables": table_text_blocks,
            "figure_captions": figure_captions,
            "images": images,
        })

    doc.close()
    return {
        "filename": os.path.basename(filepath),
        "pages": pages,
    }

def render_page_as_image(page, zoom=2):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))

def merge_text(native_text: str, ocr_text: str) -> str:
    if ocr_text.strip() in native_text:
        return native_text
    if native_text.strip() in ocr_text:
        return ocr_text
    return f"{native_text}\n\n[OCR Supplement]\n{ocr_text}"

def extract_table_blocks(data) -> list:
    """
    Group OCR text into table-like structures based on bounding box alignment.
    """
    n_boxes = len(data['text'])
    rows = []
    current_row = []
    last_top = -1

    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:
            top = data['top'][i]
            if last_top == -1 or abs(top - last_top) < 10:
                current_row.append(data['text'][i])
                last_top = top
            else:
                if current_row:
                    rows.append(" | ".join(current_row))
                current_row = [data['text'][i]]
                last_top = top
    if current_row:
        rows.append(" | ".join(current_row))
    return rows
