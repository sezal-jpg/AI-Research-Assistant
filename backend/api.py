
import logging
from backend.rag import generate_answer
from fastapi import FastAPI
from fastapi import HTTPException
from langchain_community.document_loaders import PyPDFLoader
from backend.retriever import rerank_docs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from pydantic import BaseModel
from fastapi import UploadFile, File
from typing import List

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)
embedding_model = HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")
app = FastAPI()
vectorstore = None
bm25_retriever = None
conversation_history = []
all_chunks = []
try:
    vectorstore = Chroma(persist_directory="db", embedding_function=embedding_model)
    print(" ✅ Existing Vector DB Loaded")
except Exception:
    vectorstore = None
    print("⚠️ No Existing Vector DB Found")


@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global vectorstore
    global bm25_retriever
    global all_chunks
    all_docs = []
    for file in files:
        logger.info(f"Uploaded PDF: {file.filename}")
        with open(file.filename, "wb") as f:
            f.write(await file.read())
        loader = PyPDFLoader(file.filename)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_pdf"] = file.filename
        all_docs.extend(docs)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunks = splitter.split_documents(all_docs)
    global all_chunks
    all_chunks = chunks
    logger.info(f"First Chunk Metadata: {chunks[0].metadata}")

    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embedding_model, persist_directory="db"
    )
    logger.info(f"created {len(chunks)} chunks.")
    bm25_retriever = BM25Retriever.from_documents(chunks)

    bm25_retriever.k = 3

    return {"uploaded_pdfs": len(files), "chunks": len(chunks)}


logger.info("BM25 Retriever Initialized")


class QuestionRequest(BaseModel):
    question: str
    selected_pdf: str


@app.post("/ask")
def ask_question(request: QuestionRequest):
    global vectorstore
    global bm25_retriever
    global all_chunks
    global conversation_history
    logger.info(f"selected pdf: {request.selected_pdf}")
    if vectorstore is None or bm25_retriever is None:
        raise HTTPException(
            status_code=400, detail="please upload one or more PDFs first."
        )

    # -----------------------------
    # Semantic Retrieval
    # -----------------------------
    if request.selected_pdf == "All PDFs":
        semantic_docs = vectorstore.similarity_search(request.question, k=3)
        bm25_docs = bm25_retriever.invoke(request.question)

    else:
        semantic_docs = vectorstore.similarity_search(
            request.question, k=8, filter={"source_pdf": request.selected_pdf}
        )
        filtered_chunks = [
            chunk
            for chunk in all_chunks
            if chunk.metadata["source_pdf"] == request.selected_pdf
        ]
        filtered_bm25 = BM25Retriever.from_documents(filtered_chunks)
        filtered_bm25.k = 8
        bm25_docs = filtered_bm25.invoke(request.question)

    # -----------------------------
    # Merge Results
    # -----------------------------
    docs = semantic_docs + bm25_docs
    unique_docs = []
    seen = set()
    for doc in docs:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)

    # -----------------------------
    # Reranking
    # -----------------------------
    ranked_docs = rerank_docs(request.question, unique_docs)
    if not ranked_docs:
        return {
            "answer": "I couldn't find relevant information in the uploaded PDF(s).",
            "confidence": "Very Low",
            "sources": [],
            "retrieved_chunks": 0,
        }
    top_docs = [doc for doc, score in ranked_docs[:3]]
    logger.info(f"Retrived {len(top_docs)} relevant chunks")

    sources = []
    for doc in docs:
        sources.append(
            {
                "pdf": doc.metadata.get("source_pdf", "unknown PDF"),
                "page": doc.metadata.get("page", "unknown") + 1,
            }
        )
    unique_sources = []
    seen = set()
    for source in sources:
        key = (source["pdf"], source["page"])
        if key not in seen:
            unique_sources.append(source)
            seen.add(key)

    # -----------------------------
    # Build Context
    # -----------------------------
    context = ""
    for doc in top_docs:
        source = doc.metadata.get("source_pdf", "Unknown PDF")
        page = doc.metadata.get("page", "Unknown")
        context += f"""
Source: {source}
Page: {page}
Content:
{doc.page_content}
----------------------------------------
"""

    # -----------------------------
    # Reranker Scores
    # -----------------------------
    rerank_scores = []
    for doc, score in ranked_docs[:3]:
        rerank_scores.append({"score": float(score), "content": doc.page_content[:150]})
    top_score = float(ranked_docs[0][1])
    MIN_RELEVANCE_SCORE = 1.5
    if top_score < MIN_RELEVANCE_SCORE:
        return {
            "answer": "I couldn't find relevant information in the uploaded PDF(s).",
            "confidence": "Very Low",
            "sources": [],
            "retrieved_chunks": 0,
        }
    if top_score >= 7:
        confidence = "Very high"
    elif top_score >= 5:
        confidence = "high"
    elif top_score >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    history = ""
    for chat in conversation_history[-5:]:
        history += f"""
        user: {chat['question']}
        assistant: {chat['answer']}
        """
    # -----------------------------
    # Single Gemini Call
    # -----------------------------
    try:
        answer = generate_answer(request.question, context, history)
        logger.info("Answer generated successfully.")
        # empty answer safeguard
        if not answer.strip():
            answer = "I couldn't find this information in the uploaded PDF(s)."
        bad_phrases = ["I think", "I believe", "In general", "Typically", "Usually"]
        for bad_phrase in bad_phrases:
            if bad_phrase.lower() in answer.lower():
                confidence = "Low"
                break
        logger.info(f"confidence level: {confidence}")
        conversation_history.append({"question": request.question, "answer": answer})
        logger.info("conversation history")
        logger.info(conversation_history)
        conversation_history = conversation_history[-10:]
    except Exception as e:
        logger.error(f"Gemini Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Gemini Error")
    return {
        "answer": answer,
        "retrieved_chunks": len(top_docs),
        "rerank_scores": rerank_scores,
        "sources": unique_sources,
        "confidence": confidence,
    }
