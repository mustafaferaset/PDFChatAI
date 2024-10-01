import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException
from bson import ObjectId
from app.utils.data_utils import (
    generate_unique_filename,
    save_to_mongodb,
    load_from_mongodb,
    update_mongodb
)

@pytest.fixture
def mock_db():
    return Mock()

def test_generate_unique_filename():
    with patch('os.path.exists') as mock_exists:
        # Test when file doesn't exist
        mock_exists.return_value = False
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test.pdf'

        # Test when file exists once
        mock_exists.side_effect = [True, False]
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test_1.pdf'

        # Test when file exists multiple times
        mock_exists.side_effect = [True, True, True, False]
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test_3.pdf'

def test_save_to_mongodb(mock_db):
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection
        mock_collection.insert_one.return_value.inserted_id = ObjectId('123456789012345678901234')

        data = {
            "filename": "test.pdf",
            "original_filename": "original.pdf",
            "file_path": "/path/to/test.pdf",
            "page_count": 5,
            "size_kb": 1024,
            "extracted_text": "Sample text",
        }

        result = save_to_mongodb(data)

        mock_collection.insert_one.assert_called_once_with(data)
        assert result == '123456789012345678901234'


def test_load_from_mongodb(mock_db):
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection

        # Test loading a specific PDF
        mock_collection.find_one.return_value = {"_id": ObjectId('123456789012345678901234'), "filename": "test.pdf"}
        result = load_from_mongodb('123456789012345678901234')
        assert result == {"_id": ObjectId('123456789012345678901234'), "filename": "test.pdf"}
        mock_collection.find_one.assert_called_once_with({"_id": ObjectId('123456789012345678901234')})

        # Test when PDF is not found
        mock_collection.find_one.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            load_from_mongodb('nonexistent_id')
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "PDF with ID nonexistent_id not found"

        # Test when pdf_id is not provided
        with pytest.raises(HTTPException) as exc_info:
            load_from_mongodb()
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Page Not Found"


def test_update_mongodb(mock_db):
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection

        # Test successful update
        mock_collection.update_one.return_value.modified_count = 1
        result = update_mongodb('123456789012345678901234', {"filename": "updated.pdf"})
        assert result == True
        mock_collection.update_one.assert_called_once_with(
            {"_id": ObjectId('123456789012345678901234')},
            {"$set": {"filename": "updated.pdf"}}
        )

        # Test unsuccessful update
        mock_collection.update_one.return_value.modified_count = 0
        result = update_mongodb('123456789012345678901234', {"filename": "not_updated.pdf"})
        assert result == False