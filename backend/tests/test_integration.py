# Standard library and third-party imports
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, Mock, MagicMock
from fastapi.responses import JSONResponse
from fastapi import Request
from app.utils.gemini_utils import chat_with_pdf

# Initialize FastAPI test client
client = TestClient(app)

# Fixtures for test data
@pytest.fixture
def mock_pdf_content():
    """Fixture that returns mock PDF binary content"""
    return b"%PDF-1.5\n...some pdf content..."

@pytest.fixture
def mock_extracted_text():
    """Fixture that provides sample text extracted from a mock PDF"""
    return "This is some extracted text from a PDF file."

@pytest.fixture
def mock_processed_text():
    """Fixture that simulates processed/cleaned text from a PDF"""
    return "extracted text pdf file"

@pytest.fixture
def pdf_file_path():
    """Fixture that provides a test PDF file path"""
    return "test.pdf"


def test_chat_with_nonexistent_pdf():
    """
    Test the chat endpoint's behavior when requesting a conversation with a non-existent PDF.
    Should return a 404 status code with appropriate error message.
    """
    chat_response = client.post("/v1/chat/nonexistent_id", json={
        "message": "What is this PDF about?"
    })

    assert chat_response.status_code == 404
    assert "PDF with ID nonexistent_id not found" in chat_response.json()["detail"]


def test_chat_without_pdf_id():
    """
    Test the chat endpoint when no PDF ID is provided in the URL.
    Should return a 404 status code with 'Not Found' message.
    """
    chat_response = client.post("/v1/chat/", json={
        "message": "What is this PDF about?"
    })

    assert chat_response.status_code == 404
    assert "Not Found" in chat_response.json()["detail"]


def test_rate_limiting():
    """
    Test the API's rate limiting functionality.
    Makes 61 requests to exceed the assumed rate limit of 60 requests per minute,
    then verifies that subsequent requests are blocked with a 429 status code.
    """
    # Test rate limiting by making multiple requests in quick succession
    for _ in range(61):  # Assuming the rate limit is 60 requests per minute
        client.get("/health")
    
    response = client.get("/health")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text