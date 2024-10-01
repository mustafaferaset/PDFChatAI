# PDFChatAI

## Project Overview

PDFChatAI is a sophisticated web application that enables users to interact with their PDF files through a chat interface. This innovative tool leverages advanced natural language processing to allow users to query their documents, extract specific information, and gain insights from multiple PDF files simultaneously.

## Features

- Interactive chat interface for PDF document interaction
- Multi-document support for uploading and querying multiple PDFs
- Intelligent search functionality for pinpointing specific information
- Secure document handling and user data protection
- Scalable architecture using Docker for easy deployment and scaling

## Requirements

- Python 3.10 or higher
- Docker
- Docker Compose

## Technologies

- FastAPI: High-performance web framework for building APIs
- MongoDB: NoSQL database for efficient data storage and retrieval
- Gemini 1.5 Flash: Advanced language model for natural language processing
- pypdf: Python library for reading and manipulating PDF files
- PyTest: Testing framework for ensuring code quality and reliability
- Docker & Docker Compose: Containerization for consistent deployment
- spaCy: Advanced NLP library for text processing

## Installation

1. Clone the repository:

2. Create a `.env` file in the root directory with the following configuration:
   ```
   HOST=0.0.0.0
   BACKEND_PORT=8000
   GEMINI_API_KEY=your_gemini_api_key_here
   ALLOWED_ORIGINS=["http://localhost:8000", "https://yourdomain.com"]
   MONGODB_HOST=mongodb
   MONGODB_DB=pdfchatai
   MONGODB_USER=your_mongodb_username
   MONGODB_PASSWORD=your_mongodb_password
   MONGODB_PORT=27017
   MAX_PDF_SIZE=1048576  # 1 MB
   MAX_CHAR_LENGTH=40000  # 40000 characters
   DEBUG=True
   WORKERS=1
   PDF_UPLOAD_PATH=storage/pdfs
   LOG_DIR=logs
   TOKEN_LIMIT_PER_MINUTE=100
   TOKEN_LIMIT_PER_DAY=1000
   ```
   Adjust the values according to your specific setup and requirements.

3. Build and run the application using Docker Compose:
   ```
   docker-compose up --build
   ```

4. Access the application at `http://localhost:8000` (or the port specified in your `.env` file).

## API Endpoints

### Upload PDF
- **URL**: `/v1/pdf`
- **Method**: `POST`
- **Request**:
  ```
    curl -X POST "http://localhost:8000/v1/pdf" -F "file=@{upload_file.pdf}"
  ```
- **Response**:
  ```json
  {
    "pdf_id": "66fb5a5ce4fbfd451be353d2"
  }
  ```

### Chat with PDF
- **URL**: `/v1/chat/{pdf_id}`
- **Method**: `POST`
- **Request**:
  ```json
  {
    "message": "What is the main topic of this document?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "The main topic of this document is artificial intelligence and its applications in document analysis."
  }
  ```

### Search PDF
- **URL**: `/health`
- **Method**: `GET`
- **Request**:
  ```json
  {}
  ```
- **Response**:
  ```json
    {
        "status":"healthy"
    }
  ```

## Testing

To run the test suite:

1. Ensure you're in the project root directory.
2. Run the following command:
   ```
   pytest backend/tests
   ```

This will execute all tests and provide a detailed report of the results.

## Contributing

We welcome contributions to PDFChatAI! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure your code adheres to our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
