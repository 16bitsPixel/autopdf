from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pdf_utils import extract_pdf_data
from db import collection
from models import PDFDocument

import tempfile
import shutil

app = FastAPI()


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract its data, and store it in the database.
    """
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        # Extract data from the PDF file
        pdf_data = extract_pdf_data(temp_file_path)

        # Create a PDFDocument instance
        pdf_document = PDFDocument(**pdf_data)

        # Save to MongoDB
        inserted = collection.insert_one(pdf_document.dict())

        return JSONResponse(content={"message": "PDF uploaded and data extracted successfully.", "id": str(inserted.inserted_id)}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        # Clean up the temporary file
        shutil.rmtree(temp_file_path, ignore_errors=True)

@app.get("/documents/")
def get_documents():
    """
    Retrieve all documents from the database.
    """
    docs = collection.find({}, {"filename": 1})
    return [{"id": str(doc["_id"]), "filename": doc["filename"]} for doc in docs]