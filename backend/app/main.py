from fastapi import FastAPI, Request, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.utils.pdf_utils import upload_pdf
from app.utils.gemini_utils import chat_with_pdf
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.log_config import main_logger as logger
from app.core.config import settings
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import Path

# Load environment variables
load_dotenv()

# FastAPI application
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # Add exception handler for rate limiting

# Health check endpoint
@app.get("/health", 
         response_model=dict,
         responses={
            200: {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "example": {"status": "healthy"}
                    }
                }
            }
         })
@limiter.limit("60/minute") # 60 requests per minute
async def health_check(request: Request):
    logger.info(f"Health check requested from {request.client.host}") # Log health check request
    return {"status": "healthy"}

# PDF upload endpoint
@app.post("/v1/pdf", response_model=dict,
          responses={
              200: {
                  "description": "Successful response",
                  "content": {
                      "application/json": {
                          "example": {"pdf_id": "66fb5a5ce4fbfd451be353d2"}
                      }
                  }
              },
              400: {
                  "description": "Bad Request",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Processed text exceeds maximum character length of 10000000000000"}
                      }
                  }
              }, 
              500: {
                  "description": "Internal Server Error",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Unexpected error processing PDF"}
                      }
                  }
              }
          })
@limiter.limit("5/minute") # 5 requests per minute
async def rate_limited_upload_pdf(request: Request, file: UploadFile = File(...)):
    logger.info(f"PDF upload requested from {request.client.host}") # Log PDF upload request
    return await upload_pdf(file)

# Define request model for chat
class ChatRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is the main topic of this document?"
            }
        }

# Chat with PDF endpoint
@app.post("/v1/chat/{pdf_id}", 
    response_model=dict,
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "The main topic of this document is artificial intelligence and its applications in document analysis."
                    }
                }
            }
        },
        404: {
            "description": "PDF not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "PDF with ID 123456789 not found"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Message is required in the request body"
                    }
                }
            }
        }
    }
)
@limiter.limit("10/minute") # 10 requests per minute
async def rate_limited_chat_with_pdf(
    request: Request,
    pdf_id: str = Path(..., description="The ID of the PDF to chat with"),
    chat_request: ChatRequest = Body(..., description="Chat message to send")
):
    """
    Chat with a specific PDF document.
    
    - **pdf_id**: The unique identifier of the uploaded PDF
    - **message**: The question or message to ask about the PDF content
    
    Returns the AI-generated response based on the PDF content.
    """
    logger.info(f"Chat with PDF {pdf_id} requested from {request.client.host}")
    return await chat_with_pdf(pdf_id, chat_request.message)


# Exception handlers
# HTTP exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP {exc.status_code} error for {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )
    
# Validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.url}: {exc.errors()}") # Log validation error
    return JSONResponse(
        status_code=422,
        content={"message": "Invalid request parameters", "details": exc.errors()}
    )