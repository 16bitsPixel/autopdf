from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pdf_utils import extract_pdf_data
from auto_eda import perform_eda_on_documents
from bson import ObjectId
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

@app.post("/run_eda/")
async def run_eda(document_ids: list[str]):
    """
    Run EDA only on the specified documents (by MongoDB _id).
    """
    try:
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(doc_id) for doc_id in document_ids]
        
        # Fetch only specified documents
        documents = list(collection.find({"_id": {"$in": object_ids}}))
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found for provided IDs.")

        # Perform EDA
        perform_eda_on_documents(documents)
        
        return {"message": "EDA completed successfully. Check the outputs directory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))