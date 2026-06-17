
import os
import streamlit as st
from dotenv import load_dotenv

from typing import TypedDict, List

from tavily import TavilyClient

import google.generativeai as genai

from langgraph.graph import StateGraph

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder

# LOAD ENV

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# GEMINI SETUP

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash")
reranker=CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# TAVILY


tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)



# STREAMLIT UI


st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide"
)

st.title("🔬 AI Research Assistant")

st.write(
    "Upload PDFs and ask intelligent research questions."
)

# PDF UPLOAD

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type="pdf",
    accept_multiple_files=True
)


# PROCESS PDFs


if uploaded_files:

    all_docs = []

    for file in uploaded_files:

        with open(file.name, "wb") as f:

            f.write(file.getbuffer())

        loader = PyPDFLoader(file.name)

        docs = loader.load()

        all_docs.extend(docs)

    st.success(f"Loaded {len(all_docs)} pages")


    # SPLITTING
    

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=50
    )

    chunks = splitter.split_documents(all_docs)

    st.success(f"Created {len(chunks)} chunks")


    # EMBEDDINGS
    

    embedding_model = HuggingFaceEmbeddings(

        model_name="intfloat/e5-base-v2"
    )


    # VECTOR STORE
    

    vectorstore = Chroma.from_documents(

        documents=chunks,

        embedding=embedding_model
    )

    st.success("✅ Vector DB Ready")


    # RETRIEVER
    

    semantic_retriever = vectorstore.as_retriever(

        search_type="mmr",

        search_kwargs={"k": 3}
    )
    bm25_retriever=BM25Retriever.from_documents(chunks)
    bm25_retriever.k=3
    # GRAPH STATE
    

    class GraphState(TypedDict):

        question: str

        documents: List[str]

        web_search: str

        answer: str

    # NODE 1
    

    def retrieve(state):
        

        question = state["question"]
        # BM25 Retrieval
        bm25_docs = bm25_retriever.invoke(question)
        # Semantic Retrieval
        semantic_docs = semantic_retriever.invoke(question)
        docs = bm25_docs + semantic_docs
         # remove duplicates 
        unique_docs=[]
        seen =set()
        for r in docs:
          if r.page_content not in seen:
              unique_docs.append(r)
              seen.add(r.page_content)
        # reranking 
        pairs =[(question,doc.page_content)
                for doc in unique_docs]
        scores=reranker.predict(pairs)
        ranked_docs=sorted(zip(unique_docs,scores),key=lambda x: x[1],reverse=True)    
        top_docs=[
            doc for doc,score in ranked_docs[:3]
            
        ]
        docs=[]
        for doc in top_docs:
            docs.append(f"""
        SOURCE: {doc.metadata.get('source', 'Unknown')}

        PAGE: {doc.metadata.get('page', 'Unknown')}

        CONTENT:
        {doc.page_content}
        """
        )
        return {
            'documents':docs
        }    
        
    # NODE 2
   

    def decide(state):

        docs = state["documents"]

        if len(docs) >=2:

            return "answer"

        else:

            return "web_search"

    # NODE 3
    

    def web_search(state):

        question = state["question"]

        response = tavily_client.search(

            query=question,

            max_results=3
        )

        return {

            "web_search": str(response)
        }


    # NODE 4
    
    def generate_answer(state):

        question = state["question"]

        docs = state.get("documents", [])

        web = state.get("web_search", "")

        context = "\n\n".join(docs)

        prompt = f"""
You are an intelligent AI Research Assistant.

Use available context to answer.

DOCUMENTS:
{context}

WEB SEARCH:
{web}

QUESTION:
{question}
"""

        response = model.generate_content(prompt)

        return {

            "answer": response.text
        }

    # BUILD GRAPH
    

    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", retrieve)

    workflow.add_node("web_search", web_search)

    workflow.add_node("answer", generate_answer)


    workflow.set_entry_point("retrieve")


    workflow.add_conditional_edges(

        "retrieve",

        decide,

        {

            "answer": "answer",

            "web_search": "web_search"
        }
    )


    workflow.add_edge(

        "web_search",

        "answer"
    )


    app_graph = workflow.compile()

    # USER QUESTION

    question = st.text_input(
        "Ask your question here"
    )

    # RUN GRAPH

    if question:

        with st.spinner("Researching..."):

            response = app_graph.invoke(

                {
                    "question": question
                }
            )

        # ANSWER

        st.subheader("🤖 AI Answer")

        st.write(response["answer"])


        # DOCS

        st.subheader("📄 Retrieved Chunks")

        for i, doc in enumerate(response["documents"]):

            st.markdown(f"### Chunk {i+1}")

            st.write(doc)

            st.divider()

        # WEB SEARCH

        if response.get("web_search"):

            st.subheader("🌐 Web Search Used")

            st.write(response["web_search"])

