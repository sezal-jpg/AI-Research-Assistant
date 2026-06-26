# 🔬 AI Research Assistant

An AI-powered Research Assistant built using **RAG (Retrieval-Augmented Generation)**, **LangGraph**, and **Gemini 2.5 Flash**. The application allows users to upload multiple PDF documents, ask questions in natural language, and receive context-aware answers generated from document content and web search when required.


## 🚀 Features

* 📄 Multi-PDF Upload Support
* ✂️ Intelligent Text Chunking with Overlap
* 🧠 Hugging Face Embeddings
* 🗄️ Chroma Vector Database
* 🔍 Hybrid Retrieval
  * BM25 Keyword Search
  * Semantic Search
  *  Query Rewriting
  * Query Expansion
* 🎯 Cross-Encoder Reranking
* MetaData Filtering
* Contextual Compression
* 🤖 Gemini 2.5 Flash Integration
* 🌐 Tavily Web Search Fallback
* 🔄 LangGraph Agent Workflow
* 📚 Source Attribution
* 🎨 Interactive Streamlit Interface


## 🏗️ Architecture

```text
User Question
      ↓
Query Rewriting
      ↓  
Query Expansion     
      ↓ 
Hybrid Retrieval
(BM25 + Semantic Search)
      ↓
Metadata Filtering
      ↓
Deduplication
      ↓
Cross-Encoder Reranker
      ↓
Contextual Compression
      ↓
Top Relevant Chunks
      ↓
LangGraph Agent
      ↓
Gemini 2.5 Flash
      ↓
Answer + Sources
```

## 🧠 Tech Stack

### Frontend

* Streamlit

### AI & LLM

* Gemini 2.5 Flash
* Hugging Face Embeddings
* Sentence Transformers

### Retrieval & RAG

* LangChain
* LangGraph
* ChromaDB
* BM25 Retriever
* Cross-Encoder Reranker

### Search

* Tavily Search API

### Language

* Python


## 📂 Workflow

### 1. Document Processing

* Upload PDF documents and MetaData will filter the source file
* Extract text using PyPDFLoader
* Split text into chunks using RecursiveCharacterTextSplitter

### 2. Embedding Generation

* Convert chunks into dense vector embeddings
* Store embeddings inside ChromaDB

### 3. Hybrid Retrieval

* BM25 retrieves exact keyword matches
* Semantic search retrieves contextually relevant chunks
* Results are merged and deduplicated

### 4. Reranking

* Cross-Encoder reranks retrieved chunks
* Most relevant chunks are selected

### 5. Contextual Compression

* The User's query gets compressed in a precise way to get high Quality answers and improve Retrieval.
### 5. Agent Decision

* LangGraph determines:

  * Answer from documents
  * Or use Tavily Web Search when document context is insufficient

### 6. Answer Generation

* Gemini 2.5 Flash generates final response using retrieved context


## 🎯 Key Concepts Implemented

* Retrieval-Augmented Generation (RAG)
* Chunking Strategies
* Embeddings
* Cosine Similarity
* Vector Databases
* Hybrid Retrieval
* BM25 Search
* Semantic Search
* MetaData Filtering
* Reranking
* Contextual Filtering
* Agentic Workflows
* LangGraph State Management
* LLM-Powered Question Answering


## ▶️ Installation

Clone the repository:

```bash
git clone https://github.com/sezal-jpg/AI-Research-Assistant.git
cd AI-Research-Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
TAVILY_API_KEY=your_api_key
```

Run the application:

```bash
streamlit run app.py
```


## 📈 Future Improvements

* Advanced RAG Evaluation
* Multiple Vector Database Support
* Conversation Memory
* Feedback-Based Retrieval Optimization
* Docker Deployment
* Hallucination Guard



