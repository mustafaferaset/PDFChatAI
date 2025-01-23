# Import necessary libraries for testing
import pytest
from fastapi import HTTPException
from unittest.mock import patch, Mock
from app.utils.gemini_utils import chat_with_gemini, chat_with_pdf
import google.generativeai as genai

# Fixture to mock the genai library throughout the tests
@pytest.fixture
def mock_genai():
    with patch("app.utils.gemini_utils.genai") as mock:
        yield mock

# Test successful interaction with Gemini AI
def test_chat_with_gemini_success(mock_genai):
    # Mock the Gemini AI response
    mock_genai.GenerativeModel.return_value.generate_content.return_value.text = "Test response"
    
    # Call the function with test data
    result = chat_with_gemini("Test message", "Test extracted text")
    
    # Verify the response matches the mock
    assert result == "Test response"

# Test error handling when Gemini API key is not configured
def test_chat_with_gemini_api_key_not_set(mock_genai):
    # Simulate missing API key scenario
    with patch("app.utils.gemini_utils.GEMINI_API_KEY", None):
        with pytest.raises(HTTPException) as exc_info:
            chat_with_gemini("Test message", "Test extracted text")
    
    # Verify correct error response
    assert exc_info.value.status_code == 500
    assert "Gemini API anahtarı ayarlanmadı" in str(exc_info.value.detail)

# Test successful PDF chat interaction
@pytest.mark.asyncio
async def test_chat_with_pdf_success():
    # Mock both MongoDB interaction and Gemini chat function
    with patch("app.utils.gemini_utils.load_from_mongodb") as mock_load, \
         patch("app.utils.gemini_utils.chat_with_gemini") as mock_chat:
        # Set up mock returns
        mock_load.return_value = {"extracted_text": "Test extracted text"}
        mock_chat.return_value = "Test response"
        mock_request = Mock()
        
        # Create mock async json method
        async def mock_json():
            return {"message": "Test message"}
        
        mock_request.json = mock_json
        
        # Test the PDF chat endpoint
        result = await chat_with_pdf("test_pdf_id", mock_request)
        # Verify successful response
        assert result.status_code == 200
        assert result.body == b'{"response":"Test response"}'

# Test error handling for non-existent PDF
@pytest.mark.asyncio
async def test_chat_with_pdf_not_found():
    # Mock MongoDB interaction to return None (PDF not found)
    with patch("app.utils.gemini_utils.load_from_mongodb") as mock_load:
        mock_load.return_value = None
        mock_request = Mock()
        mock_request.json.return_value = {"message": "Test message"}

        # Verify correct error handling
        with pytest.raises(HTTPException) as exc_info:
            await chat_with_pdf("non_existent_pdf_id", mock_request)

        # Check error response
        assert exc_info.value.status_code == 404
        assert "PDF with ID non_existent_pdf_id not found" in str(exc_info.value.detail)
