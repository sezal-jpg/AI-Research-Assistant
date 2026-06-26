from config import model
from rag import generate_answer
from fastapi import FastAPI
from langchain_community.document_loaders import PyPDFLoader
from retriever import rerank_docs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from pydantic import BaseModel
from fastapi import UploadFile, File
from typing import List 

embedding_model=HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")
app=FastAPI()
vectorstore=None
bm25_retriever=None

all_chunks=[]
try:
    vectorstore=Chroma(persist_directory='db',embedding_function=embedding_model)
    print(" ✅ Existing Vector DB Loaded")
except Exception:
    vectorstore=None
    print("⚠️ No Existing Vector DB Found")
    
@app.post("/upload")
async def upload_pdfs(
    files: List[UploadFile]=File(...)):
    global vectorstore
    global bm25_retriever

    all_docs = []
    for file in files:
        print(file.filename)
        with open(file.filename, "wb") as f:
          f.write(await file.read())
        loader = PyPDFLoader(file.filename)
        docs = loader.load()
        for doc in docs:
            doc.metadata['source_pdf']=file.filename
        all_docs.extend(docs)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    chunks = splitter.split_documents(all_docs)
    global all_chunks
    all_chunks=chunks
    print(chunks[0].metadata)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="db"
    )

    bm25_retriever = BM25Retriever.from_documents(
        chunks
    )

    bm25_retriever.k = 3

    return {
        "uploaded_pdfs":len(files),
        "chunks": len(chunks)
    }

 
class QuestionRequest(BaseModel):
    question: str
    selected_pdf: str


@app.post("/ask")
def ask_question(request: QuestionRequest):
    global vectorstore
    global bm25_retriever
    global all_chunks
    print("Selected PDF:", request.selected_pdf)
    if vectorstore is None:
        return {
            "error": "Please upload a PDF first"
        }

    # -----------------------------
    # Semantic Retrieval
    # -----------------------------
    if request.selected_pdf == "All PDFs":
        semantic_docs = vectorstore.similarity_search(
            request.question,
            k=3
        )
        bm25_docs = bm25_retriever.invoke(
            request.question
        )

    else:
        semantic_docs = vectorstore.similarity_search(
            request.question,
            k=3,
            filter={
                "source_pdf": request.selected_pdf
            }
        )
        filtered_chunks = [
            chunk
            for chunk in all_chunks
            if chunk.metadata["source_pdf"] == request.selected_pdf
        ]
        filtered_bm25 = BM25Retriever.from_documents(
            filtered_chunks
        )
        filtered_bm25.k = 3
        bm25_docs = filtered_bm25.invoke(
            request.question
        )

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
    ranked_docs = rerank_docs(
        request.question,
        unique_docs
    )
    top_docs = [
        doc
        for doc, score in ranked_docs[:3]
    ]

    # -----------------------------
    # Build Context
    # -----------------------------
    context = ""
    for doc in top_docs:
        source = doc.metadata.get(
            "source_pdf",
            "Unknown PDF"
        )
        page = doc.metadata.get(
            "page",
            "Unknown"
        )
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
        rerank_scores.append({
            "score": float(score),
            "content": doc.page_content[:150]
        })

    # -----------------------------
    # Single Gemini Call
    # -----------------------------
    answer = generate_answer(
        request.question,
        context
    )

    return {
        "answer": answer,
        "retrieved_chunks": len(top_docs),
        "rerank_scores": rerank_scores
    }
    











