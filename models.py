from pydantic import BaseModel
from typing import List, Optional

class ImageData(BaseModel):
    format: str
    data: str # Base64 encoded image data

class PageData(BaseModel):
    page_number: int
    text: Optional[str] = ""
    images: List[ImageData] = []

class PDFDocument(BaseModel):
    filename: str
    pages: List[PageData]
