from pydantic import BaseModel

class PDFMetadata(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    page_count: int
    size_kb: float
    extracted_text: str