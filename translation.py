import fitz  # PyMuPDF
from googletrans import Translator
import os
import asyncio

async def translate_pdf_file(input_path: str, output_dir="outputs", target_lang: str = "es"):
    """
    Translate the text of a PDF from the input path and save the translated version to output path.
    """
    doc = fitz.open(input_path)
    translator = Translator()

    # Define the output file path in the 'outputs' directory
    output_path = os.path.join(output_dir, "translated_output.pdf")
    translated_doc = fitz.open()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("dict")
        new_page = translated_doc.new_page(width=page.rect.width, height=page.rect.height)

        for block in text["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    original_text = span["text"]
                    if not original_text.strip():
                        continue
                    try:
                        # Debug: Log the original text to ensure it's being captured
                        print(f"Original text: {original_text}")

                        # Await the translation coroutine and then access the .text attribute
                        translated = await translator.translate(original_text, dest=target_lang)
                        translated_text = translated.text  # Correctly accessing the text attribute

                        # Debug: Log the translated text
                        print(f"Translated text: {translated_text}")
                    except Exception as e:
                        # Debug: Log the exception if translation fails
                        print(f"Translation failed for text: {original_text} with error: {e}")
                        translated_text = original_text

                    # Convert the color to the appropriate format (range 0-1 for RGB)
                    color = span["color"]
                    if isinstance(color, tuple) and len(color) == 4:
                        # If it's RGBA, normalize each component to [0, 1]
                        color = tuple(c / 255 for c in color[:3])  # RGB only
                    elif isinstance(color, tuple) and len(color) == 3:
                        # If it's RGB, normalize each component to [0, 1]
                        color = tuple(c / 255 for c in color)
                    else:
                        # Default to black if color is not valid
                        color = (0, 0, 0)

                    # Insert translated text with a fallback font (e.g., "helv" for Helvetica)
                    new_page.insert_text(
                        fitz.Point(span["bbox"][0], span["bbox"][1]),
                        translated_text,
                        fontsize=span["size"],
                        fontname="helv",  # Default font
                        color=color  # Corrected color format
                    )

    translated_doc.save(output_path)
    translated_doc.close()
    doc.close()

    print(f"Translated PDF saved to {output_path}")
    return output_path
