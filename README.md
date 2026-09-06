# 🌐 OmniResearch Assistant

An AI-powered, multimodal research assistant that allows users to upload documents, images, audio, video, websites, and YouTube content, ask natural-language questions, and receive grounded, context-aware answers.
The system combines hybrid retrieval, semantic search, BM25 keyword retrieval, Reciprocal Rank Fusion (RRF), Cross-Encoder reranking, Graph RAG, hierarchical context construction, and Google Gemini to produce relevant and grounded responses.
It is implemented as an agentic RAG pipeline using LangGraph and deployed using Docker and Google Cloud Run.

# 🚀 Live Demo

## 🖥️ Frontend — Streamlit

https://ai-frontend-286276858395.asia-south1.run.app/

## ⚙️ Backend API — FastAPI

https://ai-backend-286276858395.asia-south1.run.app

## 📖 API Documentation

https://ai-backend-286276858395.asia-south1.run.app/docs


# ✨ Key Features

## 📚 Multimodal Data Ingestion

The system supports multiple types of research sources:

- 📄 PDF documents
- 📝 DOCX documents
- 📊 PPTX presentations
- 📈 XLSX / XLS spreadsheets
- 📋 CSV files
- 📃 TXT files
- 📝 Markdown files
- 🔢 JSON files
- 🌐 HTML files
- 📑 XML files
- 🖼️ Images
- 🎧 Audio files
- 🎥 Video files
- 🌐 Website URLs
- ▶️ YouTube URLs

## 🔍 Hybrid Retrieval

The assistant combines multiple retrieval strategies to improve search quality.

### 🧠 Semantic Search

Uses the `intfloat/e5-base-v2` embedding model to convert documents and queries into dense vector representations.

### 🔑 BM25 Keyword Retrieval

Uses BM25 to retrieve documents based on lexical and keyword relevance.

### 🔄 Reciprocal Rank Fusion

Semantic and BM25 results are combined using Reciprocal Rank Fusion (RRF) to produce a stronger candidate set.

## 🎯 Cross-Encoder Reranking

Retrieved candidates are passed through a Cross-Encoder reranker to determine which chunks are most relevant to the user's query.

This provides an additional relevance-ranking stage before context is sent to the LLM.

## 🕸️ Graph RAG

The system includes a knowledge-graph-based retrieval layer.

During document processing:

1. Entities are extracted from document chunks.
2. Relationships between entities are identified.
3. Entities and relationships are stored in a graph.
4. Relevant graph relationships are retrieved during question answering.
5. Graph information is combined with retrieved textual context.

Example:

```text
Shadi.com
    │
    ├── uses ──> smart matchmaking system
    │
    ├── provides ──> web service
    │
    └── uses for verification ──> email verification

    🤖 Agentic RAG Pipeline

The research assistant uses LangGraph to orchestrate the question-answering workflow.

User Question
     │
     ▼
Retrieval
     │
     ▼
Rerank
     │
     ▼
Graph Retrieval
     │
     ▼
Context Building
     │
     ▼
Evaluation
   /   |   \
  /    |    \
Generate Retry Insufficient
   │      │       │
   ▼      │       ▼
 Answer   │    No Answer
          │
          ▼
    Query Refinement
          │
          └────> Retrieval

The evaluator checks whether the retrieved context provides sufficient evidence before generation.

If the evidence is insufficient, the system can refine the query, retry retrieval, or return an insufficient-information response instead of generating an unsupported answer.

🛡️ Grounding & Hallucination Protection

The system includes a generic grounding mechanism designed to prevent unsupported answers.

The evaluator considers:

retrieved context availability
meaningful query terms
lexical grounding
relationship evidence
graph evidence
retry limits

If sufficient evidence cannot be established, the system can return:

I couldn't find this information in the uploaded document(s).
📑 Source-Aware Retrieval

Users can select a specific uploaded source or all available sources.

This allows questions to be restricted to a particular document/source and helps prevent information from unrelated sources from being used.

The backend also exposes a /sources endpoint for retrieving currently indexed sources.

🧩 Hierarchical Chunking

Documents are represented using parent and child chunks.

Parent Document Section
        │
        ├── Child Chunk 1
        ├── Child Chunk 2
        ├── Child Chunk 3
        └── Child Chunk 4

Child chunks are used for precise retrieval while their parent context can be used to provide broader context during answer generation.

🧠 Conversation Memory

The assistant supports multi-turn conversations by maintaining conversation history and passing relevant previous interactions into the generation stage.

🎤 Voice Interaction

The application supports voice-based interaction.

🗣️ Speech-to-Text

Audio input can be transcribed using faster-whisper.

Voice Input
     ↓
Whisper
     ↓
Text Question
     ↓
RAG Agent
🔊 Text-to-Speech

Generated answers can also be converted into speech using the TTS pipeline.

AI Answer
    ↓
Text-to-Speech
    ↓
Audio Output
🖼️ Image Understanding

Images can be processed using vision models.

The image pipeline uses:

🤖 BLIP for image caption generation
🔎 CLIP for image embeddings

The models are loaded lazily when image processing is required, avoiding unnecessary model loading during backend startup.

🎥 Video Processing

Video sources can be processed by extracting representative frames and applying image understanding to those frames.

🌐 Website & YouTube Ingestion

The assistant can ingest web-based research sources.

🌍 Websites

Users can provide a website URL for ingestion.

▶️ YouTube

YouTube sources can be processed using available transcript information.

💾 Persistence

The application maintains persistent application state including:

indexed chunks
parent/child chunk information
Chroma vector database state
BM25 retrieval state
graph nodes and relationships
collection information

During application startup, the persistence service restores the previously indexed state.

Application Start
       │
       ▼
Persistence Service
       │
       ├── Restore Chroma
       ├── Restore Chunks
       ├── Restore Parent/Child Data
       ├── Restore BM25
       └── Restore Graph
              │
              ▼
        Ready for Queries

⚠️ Note: Local/container restart persistence is implemented. Durable cloud storage for Cloud Run is a separate architectural consideration.

🏗️ System Architecture
Streamlit Frontend
        │
        ▼
FastAPI Backend
        │
        ▼
LangGraph Agent
        │
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
   Hybrid RAG      Graph RAG    Conversation
        │              │            Memory
        ▼              ▼
 Chroma + BM25   Knowledge Graph
        │              │
        └──────┬───────┘
               ▼
       Cross-Encoder Reranker
               │
               ▼
        Context Builder
               │
               ▼
        Grounding Evaluation
          /             \
       Retry          Generate
         │                │
         └────────┐       ▼
                  └──> Gemini
                       │
                       ▼
                  Final Answer
🔄 End-to-End Processing
📥 Ingestion Pipeline
Source
  │
  ▼
Loader
  │
  ▼
Text / Content Extraction
  │
  ▼
Chunking
  │
  ▼
Parent / Child Structure
  │
  ├───────────────┐
  ▼               ▼
Embeddings      Metadata
  │
  ▼
Chroma
  │
  ▼
BM25 Index
  │
  ▼
Entity & Relationship Extraction
  │
  ▼
Knowledge Graph
❓ Question Answering Pipeline
User Question
      │
      ▼
Semantic Retrieval
      │
      ├──────────────┐
      ▼              ▼
    Chroma          BM25
      │              │
      └──────┬───────┘
             ▼
            RRF
             │
             ▼
      Cross-Encoder Reranking
             │
             ▼
       Graph Retrieval
             │
             ▼
     Hierarchical Context
             │
             ▼
         Evaluation
          /       \
       Retry     Generate
         │           │
         └──> Gemini │
                     ▼
                   Answer
🧠 Retrieval Architecture
User Query
    │
    ├──────────────┐
    ▼              ▼
Semantic Search  BM25 Search
    │              │
    └──────┬───────┘
           ▼
       RRF Fusion
           │
           ▼
    Candidate Chunks
           │
           ▼
 Cross-Encoder Reranking
           │
           ▼
   Top Relevant Chunks
           │
           ▼
    Context Builder

🕸️ Knowledge Graph Pipeline
Document Chunks
      │
      ▼
Entity Extraction
      │
      ▼
Relationship Extraction
      │
      ▼
Entity Validation
      │
      ▼
Graph Construction
      │
      ▼
Knowledge Graph
      │
      ▼
Graph Retrieval
      │
      ▼
Context Builder
🤖 LangGraph Agent Workflow
START
  │
  ▼
Retrieve
  │
  ▼
Rerank
  │
  ▼
Graph Retrieve
  │
  ▼
Context
  │
  ▼
Evaluate
  │
  ├───────────────┬────────────────┐
  ▼               ▼                ▼
Generate         Retry         Insufficient
  │               │                │
  ▼               ▼                ▼
 END          Refine Query         END
                  │
                  ▼
               Retrieve
🛠️ Technology Stack
⚙️ Backend
Python
FastAPI
LangChain
LangGraph
ChromaDB
Sentence Transformers
HuggingFace Transformers
BM25
Cross-Encoder
Google Gemini
🖥️ Frontend
Streamlit
🤖 AI / Machine Learning
Retrieval-Augmented Generation (RAG)
Hybrid Retrieval
Dense Embeddings
E5 Embeddings
BM25
Reciprocal Rank Fusion
Cross-Encoder Reranking
Graph RAG
Knowledge Graphs
BLIP
CLIP
faster-whisper
Text-to-Speech
📊 Data Processing
PyPDF
python-docx
python-pptx
OpenPyXL
Pandas
xlrd
odfpy
BeautifulSoup
OpenCV
pytesseract
☁️ Cloud
Google Cloud Run
Google Artifact Registry
Google Secret Manager
🐳 Containerization
Docker
Docker Compose
📂 Project Structure
AI Research Assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── core/
│   │   └── services/
│   │       ├── indexing_service.py
│   │       ├── persistence_service.py
│   │       ├── graph_service.py
│   │       ├── graph_query_service.py
│   │       ├── graph_retrieval_service.py
│   │       ├── blip_service.py
│   │       ├── clip_service.py
│   │       ├── image_loader.py
│   │       ├── video_loader.py
│   │       └── ...
│   ├── data/
│   │   ├── collections.json
│   │   ├── indexed_chunks.json
│   │   └── graph.json
│   ├── db/
│   ├── uploads/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── frontend.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
│
└── README.md
🐳 Docker

The application consists of two Docker services:

Docker Compose
     │
     ├── ai-backend
     │      └── FastAPI
     │
     └── ai-frontend
            └── Streamlit
▶️ Start
docker compose up -d
⏹️ Stop
docker compose down

Frontend:

http://localhost:8501

Backend:

http://localhost:8000
⚙️ Local Installation
📥 Clone Repository
git clone https://github.com/sezal-jpg/AI-Research-Assistant.git
cd AI-Research-Assistant
⚙️ Backend
cd backend
python -m venv env
🪟 Windows
env\Scripts\activate
🐧 Linux / macOS
source env/bin/activate
pip install -r requirements.txt

Create .env:

GEMINI_API_KEY=YOUR_API_KEY

Run:

uvicorn app.main:app --reload
🖥️ Frontend
cd frontend
pip install -r requirements.txt
streamlit run frontend.py
☁️ Google Cloud Deployment

The application is deployed using Google Cloud Run, Google Artifact Registry, Google Secret Manager, and Docker.

Docker Build
     ↓
Docker Image
     ↓
Artifact Registry
     ↓
Cloud Run
     ↓
Live Application
🚀 Cloud Run

The backend and frontend are deployed as separate Cloud Run services.

Current services:

Backend: ai-backend
Frontend: ai-frontend
🔐 Secret Management

The Gemini API key is not hard-coded into the application.

For local development:

GEMINI_API_KEY=YOUR_API_KEY

For Cloud Run deployment, the API key is stored in Google Secret Manager and provided to the backend through Cloud Run environment configuration.

⚠️ Never commit real API keys or secrets to source control.

🧪 Testing & Validation

The system has been tested across multiple components.

📥 Ingestion
PDF/document ingestion
PPT ingestion
Website ingestion
Multiple source indexing
🔍 Retrieval
Semantic retrieval
BM25 retrieval
Hybrid retrieval
Cross-Encoder reranking
Graph retrieval
🤖 Agent
Normal question answering
Query refinement
Retry mechanism
Insufficient-information handling
Grounding validation
📑 Source
Selected-source retrieval
All-source retrieval
Source isolation
🎤 Voice
Voice transcription
Text-to-speech
💾 Persistence
Backend restart
Chroma restoration
Chunk restoration
Parent/child restoration
BM25 restoration
Graph restoration
☁️ Deployment
Docker backend startup
Docker frontend startup
Cloud Run backend startup
Cloud Run frontend deployment
Production /docs
Production /sources
📊 Current Capabilities
📚 Data Sources

✅ PDF

✅ DOCX

✅ PPTX

✅ XLSX / XLS

✅ CSV

✅ TXT

✅ Markdown

✅ JSON

✅ HTML

✅ XML

✅ Images

✅ Audio

✅ Video

✅ Websites

✅ YouTube

🔍 Retrieval

✅ Semantic Search

✅ E5 Embeddings

✅ BM25 Retrieval

✅ Hybrid Retrieval

✅ Reciprocal Rank Fusion

✅ Cross-Encoder Reranking

🧠 RAG

✅ Hierarchical Context

✅ Source-Aware Retrieval

✅ Graph RAG

✅ Entity Extraction

✅ Relationship Extraction

🤖 Agent

✅ LangGraph Workflow

✅ Query Refinement

✅ Retry Mechanism

✅ Grounding Evaluation

✅ Insufficient Information Handling

👤 User Interaction

✅ Multi-turn Conversation

✅ Voice Input

✅ Speech-to-Text

✅ Text-to-Speech

☁️ Deployment

✅ Docker

✅ Docker Compose

✅ Google Artifact Registry

✅ Google Cloud Run

✅ Google Secret Manager

📈 Engineering Highlights



🔍 Multi-Stage Retrieval
Semantic Search
       +
BM25 Search
       ↓
RRF Fusion
       ↓
Cross-Encoder Reranking
       ↓
Context Construction
       ↓
LLM

This separates retrieval from generation and improves control over the evidence supplied to the model.

🤖 Agentic Workflow

The LangGraph workflow allows the system to evaluate retrieval quality and retry when necessary.

Question
   ↓
Retrieve
   ↓
Rerank
   ↓
Graph Retrieval
   ↓
Evaluate
   │
   ├── Sufficient → Generate
   ├── Retry → Refine → Retrieve
   └── Insufficient → Return no-answer response
🕸️ Graph-Augmented Retrieval

Traditional vector retrieval retrieves text based primarily on similarity.

Graph RAG additionally provides explicit relationships between entities.

Entity
   │
Relationship
   │
Entity
🌐 Multimodal Processing
Documents
Images
Audio
Video
Websites
YouTube
    │
    ▼
Unified Processing Layer
    │
    ▼
Retrieval System
    │
    ▼
Agent
    │
    ▼
Grounded Answer
⚠️ Known Limitations
Cloud Run instances use ephemeral local filesystems.
Durable cloud storage for uploaded files and persistent indexes requires an external persistent storage architecture.
Some multimodal processing workloads are computationally expensive.
Large document collections may require a managed vector database for horizontal scalability.
Current graph storage is application-managed rather than a dedicated managed graph database.
Authentication and multi-user isolation are not currently implemented.
Some external sources may depend on the availability of their APIs, transcripts, or web content.
LLM-based extraction and generation can be affected by API quotas and model availability.

🔮 Future Improvements
🏗️ Infrastructure
Durable cloud object storage
Managed vector database
Managed graph database
CI/CD pipeline
Kubernetes deployment
Horizontal scaling optimizations

💻 Application
Authentication
User accounts
Multi-user data isolation
Persistent user chat history
Streaming responses
Improved UI/UX
Admin dashboard
Usage analytics
User feedback system
Citation highlighting

🤖 AI
Improved OCR
Advanced multimodal reasoning
Better image-based document processing
Improved graph reasoning
Retrieval evaluation metrics
Automated evaluation pipelines
Model selection and fallback strategies

🧠 Learning Outcomes

This project demonstrates practical experience with:

Python
FastAPI
Streamlit
LangChain
LangGraph
ChromaDB
HuggingFace Embeddings
Sentence Transformers
E5 Embeddings
BM25
Reciprocal Rank Fusion
Cross-Encoder Reranking
Graph RAG
Knowledge Graph Construction
Entity Extraction
Relationship Extraction
Multimodal AI
BLIP
CLIP
Whisper
Google Gemini
Retrieval-Augmented Generation
Agentic AI
Docker
Docker Compose
Google Cloud Run
Google Artifact Registry
Google Secret Manager
Production-oriented AI system design

🎯 Project Objective

The goal of OmniResearch Assistant is to build a research-oriented AI system that goes beyond simple LLM question answering.

Instead of relying only on the model's pretrained knowledge, the system:

Ingests user-provided sources.
Processes and indexes the information.
Retrieves relevant evidence.
Combines semantic and lexical retrieval.
Reranks retrieved candidates.
Retrieves relevant graph relationships.
Builds hierarchical context.
Evaluates whether sufficient evidence exists.
Refines and retries when necessary.
Generates a grounded answer using Google Gemini.

📌 Project Summary

OmniResearch Assistant is a multimodal, agentic RAG system combining:

Multimodal Ingestion
        ↓
Hybrid Retrieval
        ↓
RRF + Reranking
        ↓
Graph RAG
        ↓
Hierarchical Context
        ↓
LangGraph Agent
        ↓
Grounding Evaluation
        │
        ├── Retry → Query Refine
        │
        └── Generate → Gemini
                         ↓
                    Final Answer

The system is containerized using Docker and deployed to Google Cloud Run.

👩‍💻 Author

Sezal Dhiman

OmniResearch Assistant — Multimodal Agentic RAG System