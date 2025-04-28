from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pdf_utils import extract_pdf_data
from auto_eda import full_eda_batch
from bson import ObjectId
from db import collection
from models import PDFDocument
from typing import List
import os

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
    
@app.post("/run_batch_eda/")
async def run_batch_eda(document_ids: List[str]):
    """
    Run EDA on multiple documents at once.
    """
    # Validate all documents exist first
    existing_docs = collection.find({"_id": {"$in": [ObjectId(doc_id) for doc_id in document_ids]}})
    existing_ids = {str(doc["_id"]) for doc in existing_docs}
    missing_ids = set(document_ids) - existing_ids

    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Documents not found: {list(missing_ids)}")

    try:
        # Run batch EDA
        stats = full_eda_batch(document_ids)

        return JSONResponse(content={
            "message": "Batch EDA completed successfully.",
            "document_stats": stats
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    file_path = os.path.join("outputs", filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
