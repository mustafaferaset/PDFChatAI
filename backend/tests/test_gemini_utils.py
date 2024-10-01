import pytest
from fastapi import HTTPException
from unittest.mock import patch, Mock
from app.utils.gemini_utils import chat_with_gemini, chat_with_pdf
import google.generativeai as genai

@pytest.fixture
def mock_genai():
    with patch("app.utils.gemini_utils.genai") as mock:
        yield mock

def test_chat_with_gemini_success(mock_genai):
    mock_genai.GenerativeModel.return_value.generate_content.return_value.text = "Test response"
    
    result = chat_with_gemini("Test message", "Test extracted text")
    
    assert result == "Test response"

def test_chat_with_gemini_api_key_not_set(mock_genai):
    # Patch the GEMINI_API_KEY to be None
    with patch("app.utils.gemini_utils.GEMINI_API_KEY", None):
        with pytest.raises(HTTPException) as exc_info:
            chat_with_gemini("Test message", "Test extracted text")
    
    assert exc_info.value.status_code == 500
    assert "Gemini API anahtarı ayarlanmadı" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_chat_with_pdf_success():
    with patch("app.utils.gemini_utils.load_from_mongodb") as mock_load, \
         patch("app.utils.gemini_utils.chat_with_gemini") as mock_chat:
        mock_load.return_value = {"extracted_text": "Test extracted text"}
        mock_chat.return_value = "Test response"
        mock_request = Mock()
        
        async def mock_json():
            return {"message": "Test message"}
        
        mock_request.json = mock_json
        
        result = await chat_with_pdf("test_pdf_id", mock_request)
        assert result.status_code == 200
        assert result.body == b'{"response":"Test response"}'

@pytest.mark.asyncio
async def test_chat_with_pdf_not_found():
    with patch("app.utils.gemini_utils.load_from_mongodb") as mock_load:
        mock_load.return_value = None
        mock_request = Mock()
        mock_request.json.return_value = {"message": "Test message"}

        with pytest.raises(HTTPException) as exc_info:
            await chat_with_pdf("non_existent_pdf_id", mock_request)

        assert exc_info.value.status_code == 404
        assert "PDF with ID non_existent_pdf_id not found" in str(exc_info.value.detail)
