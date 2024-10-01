import os
import json
from datetime import datetime
from dotenv import load_dotenv
from app.db.mongodb import get_database
from bson import ObjectId
from fastapi import HTTPException
from app.core.log_config import data_logger as logger
from bson.errors import InvalidId

load_dotenv()

def generate_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_{counter}{extension}"
        counter += 1
    return unique_filename

def save_to_mongodb(data):
    db = get_database()
    pdfs_collection = db.pdfs

    # Extract the necessary metadata
    metadata = {
        "filename": data["filename"],
        "original_filename": data["original_filename"],
        "file_path": data["file_path"],
        "page_count": data["page_count"],
        "size_kb": data["size_kb"],
        "extracted_text": data["extracted_text"],
    }

    result = pdfs_collection.insert_one(metadata)
    logger.info(f"Saved PDF to MongoDB with ID: {result.inserted_id}")
    return str(result.inserted_id)


def load_from_mongodb(pdf_id=None):
    db = get_database()
    
    if not pdf_id:
        raise HTTPException(status_code=404, detail="Page Not Found")
    try:
        return db.pdfs.find_one({"_id": ObjectId(pdf_id)})
    except InvalidId:
        logger.error(f"Invalid PDF ID: {pdf_id}")
        raise HTTPException(status_code=404, detail=f"PDF with ID {pdf_id} not found")
    except Exception as e:
        logger.error(f"Error loading PDF from MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading PDF from MongoDB: {e}")

def update_mongodb(pdf_id, data):
    db = get_database()
    pdfs_collection = db.pdfs
    result = pdfs_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": data})
    return result.modified_count > 0
