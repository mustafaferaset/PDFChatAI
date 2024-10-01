from pymongo import MongoClient
from app.core.config import settings
from app.core.log_config import mongodb_logger as logger

def get_mongodb_client():
    MONGODB_URI = f"mongodb://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}:{settings.MONGODB_PORT}/{settings.MONGODB_DB}?authSource=admin"

    client = MongoClient(MONGODB_URI)
    logger.info(f"Connected to MongoDB:")
    return client

def get_database():
    client = get_mongodb_client()
    return client[settings.MONGODB_DB]
