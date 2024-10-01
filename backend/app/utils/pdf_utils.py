import os
import uuid
from fastapi import UploadFile, HTTPException
#from PyPDF2 import PdfReader
from pypdf import PdfReader
import spacy
from app.utils.data_utils import generate_unique_filename, save_to_mongodb
from app.utils.text_processing import preprocess_text
from dotenv import load_dotenv
from app.core.log_config import pdf_logger as logger
from app.core.config import settings

load_dotenv()


PDF_UPLOAD_PATH = settings.PDF_UPLOAD_PATH
MAX_PDF_SIZE = settings.MAX_PDF_SIZE


# Create folder for uploading PDF if not exists
if not os.path.exists(PDF_UPLOAD_PATH):
    os.makedirs(PDF_UPLOAD_PATH)
    logger.info(f"Created PDF upload directory: {PDF_UPLOAD_PATH}")


async def upload_pdf(file: UploadFile):
    logger.info(f"Attempting to upload file: {file.filename}")
    validate_pdf_file(file)
    content = await file.read()
    validate_pdf_size(content, file.filename)

    try:
        file_path = save_pdf_file(content, file.filename)
        extracted_text, page_count = extract_text_from_pdf(file_path, file.filename)
        processed_text = preprocess_extracted_text(extracted_text, file.filename)

        # Check if the processed text exceeds the maximum character length
        if len(processed_text) > settings.MAX_CHAR_LENGTH:
            # Delete the file if processed text length exceeds the maximum
            os.remove(file_path)
            logger.info(f"Deleted file {file_path} due to exceeding maximum character length")
            logger.warning(f"Processed text exceeds maximum character length: {len(processed_text)}")
            raise HTTPException(status_code=400, detail=f"Processed text exceeds maximum character length of {settings.MAX_CHAR_LENGTH}")
        else:
            pdf_id = store_pdf_data(file, file_path, content, page_count, processed_text)

        logger.info(f"Successfully uploaded and processed PDF: {file.filename}")
        return {"pdf_id": pdf_id}
    except HTTPException as http_error:
        logger.error(f"HTTP error processing PDF: {str(http_error)}")
        raise http_error
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error processing PDF: {str(e)}")


def validate_pdf_file(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Rejected non-PDF file: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")


def validate_pdf_size(content: bytes, filename: str):
    if len(content) > MAX_PDF_SIZE:
        logger.warning(f"Rejected oversized PDF: {filename} ({len(content)} bytes)")
        raise HTTPException(status_code=400, detail=f"PDF file size exceeds the maximum allowed size of {MAX_PDF_SIZE / 1024 / 1024} MB")


def save_pdf_file(content: bytes, filename: str) -> str:
    unique_filename = generate_unique_filename(PDF_UPLOAD_PATH, filename)
    file_path = os.path.join(PDF_UPLOAD_PATH, unique_filename)
    logger.info(f"Writing PDF to file path: {file_path}")
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(content)
    return file_path


def extract_text_from_pdf(file_path: str, filename: str) -> tuple[str, int]:
    try:
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        
        if page_count == 0:
            logger.error(f"PDF file '{filename}' has no pages")
            raise HTTPException(status_code=400, detail="The PDF file has no pages")
        
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
        
        if not extracted_text:
            logger.error(f"No text could be extracted from '{filename}'")
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        return extracted_text, page_count
    
    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"PDF file '{filename}' not found")
    
    except PermissionError:
        logger.error(f"Permission denied when trying to read PDF file: {file_path}")
        raise HTTPException(status_code=403, detail=f"Permission denied when trying to read PDF file '{filename}'")
    
    except HTTPException as http_error:
        logger.error(f"HTTP error processing PDF: {str(http_error)}")
        raise http_error
    except Exception as e:
        logger.error(f"Error extracting text from PDF '{filename}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF file '{filename}'")


def preprocess_extracted_text(extracted_text: str, filename: str) -> str:
    try:
        nlp = spacy.load("en_core_web_sm")
        return preprocess_text(extracted_text, nlp)
    except Exception as nlp_error:
        logger.error(f"Error preprocessing text: {str(nlp_error)}")
        raise HTTPException(status_code=500, detail=f"Error preprocessing text: {str(nlp_error)}")


def store_pdf_data(file: UploadFile, file_path: str, content: bytes, page_count: int, processed_text: str) -> str:
    data_store = {
        "filename": os.path.basename(file_path),
        "original_filename": file.filename,
        "file_path": file_path,
        "page_count": page_count,
        "size_kb": len(content) / 1024,
        "extracted_text": processed_text,
    }
    return save_to_mongodb(data_store)
