# 🔬 AI Research Assistant

An AI-powered Research Assistant that allows users to upload one or multiple PDF documents, ask natural language questions, and receive context-aware answers using Retrieval-Augmented Generation (RAG).

The application combines semantic search, keyword search, reranking, and Google's Gemini LLM to provide accurate answers with confidence scores and source citations.


## 🚀 Live Demo

### Frontend (Streamlit)
https://ai-frontend-286276858395.asia-south1.run.app/

### Backend API (FastAPI)
https://ai-backend-286276858395.asia-south1.run.app


# ✨ Features

- 📄 Upload one or multiple PDF documents
- 🔍 Semantic Search using E5 Embeddings
- 📚 BM25 Keyword Retrieval
- ⚡ Hybrid Retrieval (Semantic + BM25)
- 🎯 Cross-Encoder Reranking
- 🤖 Google Gemini powered answer generation
- 💬 Multi-turn conversation history
- 📑 Source page citations
- 📊 Confidence score estimation
- 📂 Search within a selected PDF or across all uploaded PDFs
- ☁️ Dockerized backend and frontend
- 🚀 Deployed on Google Cloud Run


# 🏗️ Architecture

                Streamlit Frontend
                        │
                        ▼
                 FastAPI Backend
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Chroma Vector DB   BM25 Retriever   Gemini API
        │
        ▼
 Cross Encoder Reranker
        │
        ▼
   Final AI Response


# 🛠️ Tech Stack

## Backend

- FastAPI
- LangChain
- ChromaDB
- Sentence Transformers
- HuggingFace Embeddings
- Google Gemini API
- BM25 Retriever
- Cross Encoder Reranker

## Frontend

- Streamlit

## AI & Machine Learning

- Retrieval-Augmented Generation (RAG)
- Hybrid Retrieval
- Semantic Search
- Dense Embeddings
- Cross Encoder Reranking

## Cloud

- Google Cloud Run
- Google Artifact Registry

## Containerization

- Docker
- Docker Compose


# 📂 Project Structure

AI Research Assistant/
│
├── backend/
│   ├── api.py
│   ├── rag.py
│   ├── retriever.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── frontend.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md



# ⚙️ Installation

## Clone Repository


git clone https://github.com/sezal-jpg/AI-Research-Assistant.git

cd AI-Research-Assistant


## Backend Setup

cd backend

python -m venv venv

source venv/bin/activate

Windows

venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Create `.env`

GOOGLE_API_KEY=YOUR_API_KEY


Run

uvicorn api:app --reload


## Frontend Setup

cd frontend

pip install -r requirements.txt

streamlit run frontend.py


# 🐳 Docker

## Build Backend

docker build -t ai-backend .


Run

docker run -p 8080:8080 ai-backend


## Build Frontend

docker build -t ai-frontend .


Run

docker run -p 8501:8501 ai-frontend


# ☁️ Google Cloud Deployment

The application is fully deployed using:

- Google Cloud Run
- Google Artifact Registry
- Docker Containers

Deployment workflow:

Docker Build
      ↓
Docker Push
      ↓
Artifact Registry
      ↓
Cloud Run
      ↓
Live Application


# 📖 How It Works

### Step 1

Upload one or multiple PDF documents.

### Step 2

Documents are split into chunks.

### Step 3

Each chunk is converted into embeddings using:

intfloat/e5-base-v2


### Step 4

Chunks are stored inside Chroma Vector Database.

### Step 5

When a user asks a question:

- Semantic Search retrieves relevant chunks.
- BM25 retrieves keyword-based matches.
- Results are merged.

### Step 6

Cross Encoder reranks retrieved chunks.

### Step 7

Top ranked chunks are passed to Gemini.

### Step 8

Gemini generates a grounded answer with:

- Confidence score
- Source citations



# 📈 Current Capabilities

✅ Multi PDF Support

✅ Hybrid Retrieval

✅ Semantic Search

✅ BM25 Retrieval

✅ Cross Encoder Reranking

✅ Source Citations

✅ Conversation Memory

✅ Confidence Estimation

✅ Google Gemini Integration

✅ Docker Deployment

✅ Cloud Deployment


# 🔮 Future Improvements

- Authentication
- User Accounts
- Cloud Storage for PDFs
- Persistent Vector Database
- Streaming Responses
- Better UI/UX
- Chat History
- Admin Dashboard
- Usage Analytics
- Feedback System
- Citation Highlighting
- OCR Support
- Image-based PDF Support
- Multi-modal RAG
- CI/CD Pipeline
- Kubernetes Deployment


# 🧠 Learning Outcomes

This project demonstrates practical experience with:

- FastAPI
- Streamlit
- LangChain
- ChromaDB
- HuggingFace Embeddings
- Sentence Transformers
- Hybrid Retrieval
- Cross Encoder Reranking
- Google Gemini API
- Docker
- Google Cloud Run
- Artifact Registry
- Production Deployment
- Retrieval-Augmented Generation (RAG)
