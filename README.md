# RAG Chatbot with Flask, ChromaDB, and Streamlit

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Flask for the API, ChromaDB as the vector database, and Streamlit for the frontend.

## Features
- **Document Upload:** Users can upload PDF, TXT, or DOCX files.
- **Chatbot Interface:** Streamlit-based UI for interactive conversations.
- **Retrieval-Augmented Generation:** Uses document context for better responses.
- **History Support:** Option to use chat history in responses.

## Setup Instructions

### Prerequisites
- Docker & Docker Compose installed
- GitHub Codespaces (if using Codespaces)

### Running with Docker Compose

1. Clone the repository:
   ```bash
   git clone [https://github.com/moustafa-ismail/applab.git](https://github.com/moustafa-ismail/applab.git)
   cd applab
   ```
2. Start the containers:
   ```bash
   docker-compose up --build -d
   ```
3. Open Streamlit UI at:
   ```
   http://localhost:8088
   ```

## API Documentation

### 1. Upload Document
**Endpoint:** `POST /upload/`  
**Description:** Uploads and processes a document.  
**Payload:** `multipart/form-data` with a `file` field.  
**Response:**  
```json
{ "message": "File uploaded successfully" }
```

### 2. Chatbot Query
**Endpoint:** `POST /chat/`  
**Description:** Sends a query and retrieves a response using RAG.  
**Payload:**  
```json
{ "question": "What is AI?", "use_documents": true }
```
**Response:**  
```json
{
  "answer": "AI stands for Artificial Intelligence...",
  "sources": ["source1.pdf", "source2.txt"]
}
```

## Development Notes
- The chatbot retrieves relevant document chunks from ChromaDB and passes them to the LLM.
- The UI allows toggling document usage in responses.
- Source documents are displayed in a collapsible section.

## License
MIT License
