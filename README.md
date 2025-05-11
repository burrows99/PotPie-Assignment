# PotPie Assignment

A Node.js backend for document processing, semantic search, and conversational chat with Retrieval-Augmented Generation (RAG) using ChromaDB and Ollama.

## Features
- User authentication (register, login)
- Secure document upload and processing with embeddings stored in ChromaDB
- Vector search and RAG-powered chat (Ollama LLM, TinyLlama model)
- All endpoints use async/await and robust error handling
- Dockerized startup for ChromaDB and Ollama (auto-run)

---

## Project Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/burrows99/PotPie-Assignment.git
   cd PotPie-Assignment
   ```
2. **Install dependencies**
   ```sh
   npm install
   ```
3. **Environment variables**
   - Copy `.env.example` to `.env` and fill in required values (DB, JWT, etc).
4. **Start the server**
   ```sh
   npm start
   ```
   - The server will auto-start ChromaDB and Ollama containers if not running.

---

## API Endpoints

### Auth
- `POST /auth/register` — Register a new user. `{ email, password }`
- `POST /auth/login` — Login and get JWT. `{ email, password }`

### Documents
- `POST /documents/process` — Upload and process a document (PDF, DOCX, TXT). Returns `assetId`.
  - **Headers:** `Authorization: Bearer <token>`
  - **Body:** `multipart/form-data` with file under `file` field.

### Chat (RAG)
- `POST /chat` — Chat with LLM (optionally with asset context)
  - **Headers:** `Authorization: Bearer <token>`
  - **Body:**
    ```json
    {
      "message": "Your question here",
      "assetIds": ["asset-id-1", "asset-id-2"] // optional
    }
    ```
- `GET /chat/threads` — List user chat threads
- `GET /chat/threads/:threadId/messages` — Get messages for a thread

---

## LangChain & RAG Capabilities
- Embeddings are created for uploaded documents and stored in ChromaDB.
- Chat endpoint retrieves relevant context from ChromaDB using asset IDs and injects it into the LLM prompt.
- Uses Ollama (TinyLlama) for conversational responses.

---

## Error Handling & Edge Cases
- All endpoints validate input and return meaningful error messages (400/401/500).
- Async/await is used throughout; errors are caught and logged.
- Docker startup of ChromaDB/Ollama is checked and logged; server exits if dependencies are unavailable.

---

## Evaluation Criteria
- **Code quality and organization**: Modular, clear, and maintainable.
- **Async operations**: All DB/LLM/embedding calls are async and properly handled.
- **LangChain/RAG**: Embedding, vector search, and context injection in chat.
- **Requirements**: All functional and technical requirements are met.
- **API design & docs**: RESTful, documented above.
- **Error handling**: Robust, with edge case consideration.

---

## Example Usage

1. Register/login to get a JWT.
2. Upload a document via `/documents/process`.
3. Chat with the LLM using `/chat`, providing asset IDs for RAG.

---

## Notes
- Ensure Docker is running for ChromaDB and Ollama containers.
- The project is ready for local development and further extension.
