import google.generativeai as genai
from fastapi import HTTPException, Request
import json
import logging
from app.utils.data_utils import load_from_mongodb
from dotenv import load_dotenv
import time
from fastapi.responses import JSONResponse
from app.core.log_config import gemini_logger as logger
from app.core.config import settings

import os

# Load environment variables
load_dotenv()

# Google Gemini API key
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Initialize the Google Generative AI Client with the API key
genai.configure(api_key=GEMINI_API_KEY)

TOKEN_LIMIT_PER_MINUTE = settings.TOKEN_LIMIT_PER_MINUTE
TOKEN_LIMIT_PER_DAY = settings.TOKEN_LIMIT_PER_DAY



# Token bucket algorithm for rate limiting
class TokenBucket:
    def __init__(self, tokens_per_minute, tokens_per_day):
        self.tokens_per_minute = tokens_per_minute
        self.tokens_per_day = tokens_per_day
        self.tokens = tokens_per_day
        self.last_refill = time.time()

    def consume(self, tokens):
        now = time.time()
        time_passed = now - self.last_refill
        self.tokens = min(self.tokens_per_day, self.tokens + time_passed * (self.tokens_per_minute / 60))
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

token_bucket = TokenBucket(TOKEN_LIMIT_PER_MINUTE, TOKEN_LIMIT_PER_DAY)

# Chat with Gemini
def chat_with_gemini(message, extracted_text):
    if not GEMINI_API_KEY:
        logger.error("Gemini API anahtarı ayarlanmadı")
        raise HTTPException(status_code=500, detail="Gemini API anahtarı ayarlanmadı")
    try:
        # Define model parameters
        generation_config = genai.GenerationConfig(
            temperature=0.7, 
            top_p=0.9,
            top_k=40,
            max_output_tokens=8192
        )
        logger.info(f"Generation config: {generation_config}")
        # Define safety settings
        safety_settings = [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            }
        ]
        logger.info(f"Safety settings: {safety_settings}")
        # Initialize the model with the defined parameters
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        logger.info(f"Model initialized: {model}")
        # Construct the user prompt
        # Construct a more detailed prompt for better answers
        prompt = f"""
        PDF Content: {extracted_text}

        User Question: {message}

        Instructions:
        1. Carefully analyze the PDF content provided above.
        2. Focus on answering the user's question accurately and comprehensively.
        3. If the answer is directly stated in the PDF, quote the relevant part.
        4. If the answer requires interpretation, explain your reasoning clearly.
        5. If the PDF doesn't contain enough information to answer the question, state this clearly.
        6. Provide context and additional information when relevant.
        7. Keep your response concise but informative.
        8. If appropriate, suggest follow-up questions the user might find helpful.

        Please provide your response based on these instructions:
        """

        response = model.generate_content([prompt])
        logger.info(f"ResponseXXX: {response}")
        tokens_used = len(response.text.split())  # Simple estimation of tokens used

        if not token_bucket.consume(tokens_used):
            logger.error("Token limit exceeded")
            raise HTTPException(status_code=429, detail="Token limit exceeded")
        return response.text.strip()
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=f"Unexpected error in chat_with_gemini: {error_message}")


async def chat_with_pdf(pdf_id: str, message: str):
    logger.info(f"Chat request for PDF {pdf_id}")
    try:
        pdf_data = load_from_mongodb(pdf_id=pdf_id)
        
        if pdf_data is None:
            raise HTTPException(status_code=404, detail=f"PDF with ID {pdf_id} not found")
        
        logger.info(f"PDF data retrieved from MongoDB: {pdf_data}")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        # Check if pdf_data is a dictionary and has the 'extracted_text' key
        if not isinstance(pdf_data, dict):
            logger.error(f"Invalid PDF data structure: {pdf_data}")
            raise HTTPException(status_code=500, detail="Invalid PDF data structure")

        if 'extracted_text' not in pdf_data:
            logger.error(f"Invalid PDF data structure: {pdf_data}")
            raise HTTPException(status_code=500, detail="Invalid PDF data structure")

        extracted_text = pdf_data.get("extracted_text")
        if not extracted_text or len(extracted_text.strip()) == 0: # Check if extracted text is empty
            logger.error("Extracted text is empty for the given PDF")
            raise HTTPException(status_code=400, detail="Extracted text is empty for the given PDF")
        
        # TODO make more efficient by using a more efficient tokenization method
        max_length = 10000000000000 # Set max length for extracted text
        if len(extracted_text) > max_length: # Check if extracted text is too long
            extracted_text = extracted_text[:max_length] + "..." # Truncate extracted text
            logger.warning(f"Extracted text was truncated from {len(extracted_text)} to {max_length} characters")

        response = chat_with_gemini(message, extracted_text) # Chat with Gemini
        logger.info(f"Successfully processed chat request for PDF {pdf_id}")
        return JSONResponse(content={"response": response})

    except HTTPException as he: # HTTP exception
        logger.error(f"HTTP exception in chat_with_pdf: {he.detail}")
        raise he
    except json.JSONDecodeError: # JSON decode error
        logger.error(f"Invalid JSON in request body for PDF {pdf_id}")
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e: # Exception
        logger.error(f"Unexpected error in chat_with_pdf: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")