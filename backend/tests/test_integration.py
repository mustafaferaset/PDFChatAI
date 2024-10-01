import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, Mock, MagicMock
from fastapi.responses import JSONResponse
from fastapi import Request
from app.utils.gemini_utils import chat_with_pdf

client = TestClient(app)

@pytest.fixture
def mock_pdf_content():
    return b"%PDF-1.5\n...some pdf content..."

@pytest.fixture
def mock_extracted_text():
    return "This is some extracted text from a PDF file."

@pytest.fixture
def mock_processed_text():
    return "extracted text pdf file"

@pytest.fixture
def pdf_file_path():
    return "test.pdf"


def test_chat_with_nonexistent_pdf():
    chat_response = client.post("/v1/chat/nonexistent_id", json={
        "message": "What is this PDF about?"
    })

    assert chat_response.status_code == 404
    assert "PDF with ID nonexistent_id not found" in chat_response.json()["detail"]


def test_chat_without_pdf_id():
    chat_response = client.post("/v1/chat/", json={
        "message": "What is this PDF about?"
    })

    assert chat_response.status_code == 404
    assert "Not Found" in chat_response.json()["detail"]


def test_rate_limiting():
    # Test rate limiting by making multiple requests in quick succession
    for _ in range(61):  # Assuming the rate limit is 60 requests per minute
        client.get("/health")
    
    response = client.get("/health")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text