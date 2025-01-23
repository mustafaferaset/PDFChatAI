# Import necessary testing and mocking utilities
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

# Fixture to create a mock database instance for testing
@pytest.fixture
def mock_db():
    return Mock()

def test_generate_unique_filename():
    """Test the generation of unique filenames to avoid duplicates"""
    with patch('os.path.exists') as mock_exists:
        # Scenario 1: Test when file doesn't exist
        # Should return the original filename
        mock_exists.return_value = False
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test.pdf'

        # Scenario 2: Test when file exists once
        # Should append _1 to the filename
        mock_exists.side_effect = [True, False]
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test_1.pdf'

        # Scenario 3: Test when file exists multiple times
        # Should increment counter until finding an available filename
        mock_exists.side_effect = [True, True, True, False]
        result = generate_unique_filename('/test/dir', 'test.pdf')
        assert result == 'test_3.pdf'

def test_save_to_mongodb(mock_db):
    """Test saving PDF metadata to MongoDB"""
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection
        # Mock the ObjectId that MongoDB would generate
        mock_collection.insert_one.return_value.inserted_id = ObjectId('123456789012345678901234')

        # Sample PDF metadata to be saved
        data = {
            "filename": "test.pdf",
            "original_filename": "original.pdf",
            "file_path": "/path/to/test.pdf",
            "page_count": 5,
            "size_kb": 1024,
            "extracted_text": "Sample text",
        }

        result = save_to_mongodb(data)

        # Verify the data was saved correctly
        mock_collection.insert_one.assert_called_once_with(data)
        assert result == '123456789012345678901234'

def test_load_from_mongodb(mock_db):
    """Test loading PDF metadata from MongoDB"""
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection

        # Scenario 1: Test successfully loading a specific PDF
        mock_collection.find_one.return_value = {"_id": ObjectId('123456789012345678901234'), "filename": "test.pdf"}
        result = load_from_mongodb('123456789012345678901234')
        assert result == {"_id": ObjectId('123456789012345678901234'), "filename": "test.pdf"}
        mock_collection.find_one.assert_called_once_with({"_id": ObjectId('123456789012345678901234')})

        # Scenario 2: Test when PDF is not found
        # Should raise 404 HTTPException
        mock_collection.find_one.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            load_from_mongodb('nonexistent_id')
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "PDF with ID nonexistent_id not found"

        # Scenario 3: Test when no pdf_id is provided
        # Should raise 404 HTTPException
        with pytest.raises(HTTPException) as exc_info:
            load_from_mongodb()
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Page Not Found"

def test_update_mongodb(mock_db):
    """Test updating PDF metadata in MongoDB"""
    with patch('app.utils.data_utils.get_database', return_value=mock_db):
        mock_collection = Mock()
        mock_db.pdfs = mock_collection

        # Scenario 1: Test successful update
        # Should return True when document is modified
        mock_collection.update_one.return_value.modified_count = 1
        result = update_mongodb('123456789012345678901234', {"filename": "updated.pdf"})
        assert result == True
        mock_collection.update_one.assert_called_once_with(
            {"_id": ObjectId('123456789012345678901234')},
            {"$set": {"filename": "updated.pdf"}}
        )

        # Scenario 2: Test unsuccessful update
        # Should return False when no document is modified
        mock_collection.update_one.return_value.modified_count = 0
        result = update_mongodb('123456789012345678901234', {"filename": "not_updated.pdf"})
        assert result == False