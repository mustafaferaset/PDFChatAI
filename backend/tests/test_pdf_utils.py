import pytest
from fastapi import UploadFile, HTTPException
from unittest.mock import Mock, patch, mock_open
from app.utils.pdf_utils import (
    upload_pdf,
    validate_pdf_file,
    validate_pdf_size,
    save_pdf_file,
    extract_text_from_pdf,
    preprocess_extracted_text,
    store_pdf_data
)
from app.core.config import settings

@pytest.fixture
def mock_pdf_file():
    # Creates a mock UploadFile object for testing
    return Mock(spec=UploadFile, filename="test.pdf")

@pytest.fixture
def mock_content():
    # Creates mock PDF binary content for testing
    return b"Mock PDF content"

@pytest.mark.asyncio
async def test_upload_pdf_success(mock_pdf_file, mock_content):
    # Tests successful PDF upload flow with mocked dependencies
    mock_pdf_file.read.return_value = mock_content
    with patch("app.utils.pdf_utils.save_pdf_file") as mock_save, \
         patch("app.utils.pdf_utils.extract_text_from_pdf") as mock_extract, \
         patch("app.utils.pdf_utils.preprocess_extracted_text") as mock_preprocess, \
         patch("app.utils.pdf_utils.store_pdf_data") as mock_store:
        
        mock_save.return_value = "/path/to/saved/file.pdf"
        mock_extract.return_value = ("Extracted text", 1)
        mock_preprocess.return_value = "Processed text"
        mock_store.return_value = "pdf_id_123"

        result = await upload_pdf(mock_pdf_file)
        assert result == {"pdf_id": "pdf_id_123"}

@pytest.mark.asyncio
async def test_upload_pdf_invalid_file(mock_pdf_file):
    # Tests rejection of non-PDF file upload
    mock_pdf_file.filename = "invalid.txt"
    with pytest.raises(HTTPException) as exc_info:
        await upload_pdf(mock_pdf_file)
    assert exc_info.value.status_code == 400
    assert "Only PDF files are accepted" in str(exc_info.value.detail)

def test_validate_pdf_file_success(mock_pdf_file):
    # Tests successful PDF file validation
    validate_pdf_file(mock_pdf_file)  # Should not raise an exception

def test_validate_pdf_file_failure():
    # Tests rejection of invalid file type
    invalid_file = Mock(spec=UploadFile, filename="test.txt")
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf_file(invalid_file)
    assert exc_info.value.status_code == 400
    assert "Only PDF files are accepted" in str(exc_info.value.detail)

def test_validate_pdf_size_success(mock_content):
    # Tests successful PDF size validation
    validate_pdf_size(mock_content, "test.pdf")  # Should not raise an exception

def test_validate_pdf_size_failure():
    # Tests rejection of PDF exceeding maximum size limit
    large_content = b"a" * (settings.MAX_PDF_SIZE + 1)
    with pytest.raises(HTTPException) as exc_info:
        validate_pdf_size(large_content, "large.pdf")
    assert exc_info.value.status_code == 400
    assert "PDF file size exceeds the maximum allowed size" in str(exc_info.value.detail)

def test_validate_pdf_size_at_limit():
    # Tests PDF file exactly at size limit is accepted
    content = b"a" * settings.MAX_PDF_SIZE
    validate_pdf_size(content, "at_limit.pdf")  # Should not raise an exception

def test_save_pdf_file(mock_content):
    # Tests PDF file saving functionality with mocked file operations
    with patch("app.utils.pdf_utils.generate_unique_filename") as mock_generate, \
         patch("builtins.open", mock_open()) as mock_file:
        mock_generate.return_value = "unique_test.pdf"
        file_path = save_pdf_file(mock_content, "test.pdf")
        assert file_path == f"{settings.PDF_UPLOAD_PATH}/unique_test.pdf"
        mock_file.assert_called_once_with(file_path, "wb")
        mock_file().write.assert_called_once_with(mock_content)

@patch("app.utils.pdf_utils.PdfReader")
def test_extract_text_from_pdf_success(mock_pdf_reader):
    # Tests successful text extraction from PDF with multiple pages
    mock_pdf_reader.return_value.pages = [Mock(extract_text=lambda: "Page 1 text"), Mock(extract_text=lambda: "Page 2 text")]
    with patch("builtins.open", mock_open()):
        extracted_text, page_count = extract_text_from_pdf("/path/to/test.pdf", "test.pdf")
    assert extracted_text == "Page 1 textPage 2 text"
    assert page_count == 2

@patch("app.utils.pdf_utils.PdfReader")
def test_extract_text_from_pdf_no_text(mock_pdf_reader):
    # Tests handling of PDF with no extractable text
    mock_pdf_reader.return_value.pages = [Mock(extract_text=lambda: "")]
    with patch("builtins.open", mock_open()):
        with pytest.raises(HTTPException) as exc_info:
            extract_text_from_pdf("/testfiles/empty.pdf", "empty.pdf")
    assert exc_info.value.status_code == 400
    assert "No text could be extracted from the PDF" in str(exc_info.value.detail)

@patch("app.utils.pdf_utils.PdfReader")
def test_extract_text_from_pdf_multiple_pages(mock_pdf_reader):
    # Tests text extraction from PDF with three pages
    mock_pdf_reader.return_value.pages = [
        Mock(extract_text=lambda: "Page 1 text"),
        Mock(extract_text=lambda: "Page 2 text"),
        Mock(extract_text=lambda: "Page 3 text")
    ]
    with patch("builtins.open", mock_open()):
        extracted_text, page_count = extract_text_from_pdf("/path/to/test.pdf", "test.pdf")
    assert extracted_text == "Page 1 textPage 2 textPage 3 text"
    assert page_count == 3

def test_preprocess_extracted_text():
    # Tests text preprocessing with spaCy
    with patch("app.utils.pdf_utils.spacy.load") as mock_load, \
         patch("app.utils.pdf_utils.preprocess_text") as mock_preprocess:
        mock_nlp = Mock()
        mock_load.return_value = mock_nlp
        mock_preprocess.return_value = "Processed text"
        
        result = preprocess_extracted_text("Raw text", "test.pdf")
        assert result == "Processed text"
        mock_load.assert_called_once_with("en_core_web_sm")
        mock_preprocess.assert_called_once_with("Raw text", mock_nlp)

def test_preprocess_extracted_text_empty():
    # Tests preprocessing of empty text
    with patch("app.utils.pdf_utils.spacy.load") as mock_load, \
         patch("app.utils.pdf_utils.preprocess_text") as mock_preprocess:
        mock_nlp = Mock()
        mock_load.return_value = mock_nlp
        mock_preprocess.return_value = ""
        
        result = preprocess_extracted_text("", "empty.pdf")
        assert result == ""
        mock_load.assert_called_once_with("en_core_web_sm")
        mock_preprocess.assert_called_once_with("", mock_nlp)

def test_store_pdf_data():
    # Tests storing PDF metadata in MongoDB
    mock_file = Mock(spec=UploadFile, filename="original.pdf")
    with patch("app.utils.pdf_utils.save_to_mongodb") as mock_save:
        mock_save.return_value = "pdf_id_123"
        result = store_pdf_data(mock_file, "/path/to/file.pdf", b"content", 2, "Processed text")
        assert result == "pdf_id_123"
        mock_save.assert_called_once_with({
            "filename": "file.pdf",
            "original_filename": "original.pdf",
            "file_path": "/path/to/file.pdf",
            "page_count": 2,
            "size_kb": len(b"content") / 1024,
            "extracted_text": "Processed text",
        })

def test_store_pdf_data_large_file():
    # Tests storing metadata for a large PDF file
    mock_file = Mock(spec=UploadFile, filename="large.pdf")
    large_content = b"a" * (10 * 1024 * 1024)  # 10 MB
    with patch("app.utils.pdf_utils.save_to_mongodb") as mock_save:
        mock_save.return_value = "pdf_id_large"
        result = store_pdf_data(mock_file, "/path/to/large.pdf", large_content, 100, "Large processed text")
        assert result == "pdf_id_large"
        mock_save.assert_called_once_with({
            "filename": "large.pdf",
            "original_filename": "large.pdf",
            "file_path": "/path/to/large.pdf",
            "page_count": 100,
            "size_kb": len(large_content) / 1024,
            "extracted_text": "Large processed text",
        })
