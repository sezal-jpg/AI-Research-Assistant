
# 🔬 AI Research Assistant

An AI-powered research assistant built using:

- LangGraph
- RAG (Retrieval-Augmented Generation)
- Gemini API
- Chroma Vector Database
- Streamlit
- Tavily Web Search


# 🚀 Features

✅ Upload multiple PDFs  
✅ Semantic document retrieval  
✅ Vector embeddings using HuggingFace  
✅ LangGraph agent workflow  
✅ Conditional routing  
✅ Web search fallback  
✅ Gemini-powered grounded answers  
✅ Streamlit UI  


# 🧠 Architecture

User Question
↓
PDF Retrieval (RAG)
↓
Decision Node
├── Enough Context → Answer
└── Not Enough → Tavily Web Search
↓
Gemini Final Response


# 📦 Tech Stack

- Python
- Streamlit
- LangChain
- LangGraph
- ChromaDB
- HuggingFace Embeddings
- Gemini API
- Tavily API


# ⚙️ Installation

git clone <your_repo_url>

cd AI-Research-Assistant

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt


# 🔑 Environment Variables

Create a `.env` file:

GEMINI_API_KEY=your_key

TAVILY_API_KEY=your_key


# ▶️ Run App

streamlit run app.py



# 📸 Demo

(Add screenshots here later)


# 🚀 Future Improvements

* Conversational memory
* Multi-agent workflows
* Hybrid search
* Reranking
* Deployment

