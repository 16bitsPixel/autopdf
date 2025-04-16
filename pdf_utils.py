import fitz
import base64

def extract_pdf_data(filepath: str) -> dict:
    doc = fitz.open(filepath)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_format = base_image["ext"]
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            images.append({"format": image_format, "data": encoded_image})
        
        pages.append({"page_number": i + 1, "text": text, "images": images})
    doc.close()
    return {"filename": filepath.split("/")[-1], "pages": pages}
