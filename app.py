
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
from langchain_core.documents import Document

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
with st.sidebar:
    st.header("📊 Project Information")

    st.write("🤖 Model: Gemini 2.5 Flash")
    st.write("🗄️ Vector DB: ChromaDB")
    st.write("🔍 Retrieval: BM25 + Semantic Search")
    st.write("🧠 Framework: LangGraph")
    st.write("🌐 Search Tool: Tavily")
# PDF UPLOAD

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type="pdf",
    accept_multiple_files=True
)
pdf_names=[file.name for file in uploaded_files]
selected_pdf=st.selectbox('Filter by PDF',['All PDFs'] + pdf_names)
st.info(f'Active Filter: {selected_pdf}')
# PROCESS PDFs


if uploaded_files:

    all_docs = []

    for file in uploaded_files:

        with open(file.name, "wb") as f:

            f.write(file.getbuffer())

        loader = PyPDFLoader(file.name)

        docs = loader.load()

        all_docs.extend(docs)
    with st.sidebar:
     st.success(f"Loaded {len(all_docs)} pages")


    # SPLITTING
    

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=50
    )

    chunks = splitter.split_documents(all_docs)
    with st.sidebar:
     st.success(f"Created {len(chunks)} chunks")


    # EMBEDDINGS
    

    embedding_model = HuggingFaceEmbeddings(

        model_name="intfloat/e5-base-v2"
    )


    # VECTOR STORE
    

    vectorstore = Chroma.from_documents(

        documents=chunks,

        embedding=embedding_model,
        persist_directory='db'
    )
    with st.sidebar:
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
        selected_pdf:str
        rewritten_query: str
        documents: List[Document]
        rerank_scores: List
        top_score:float
        compressed_docs: List[str]
        web_search: str
        answer: str
        
        # query rewriting
    @st.cache_data    
    def rewrite_query(question: str):
        prompt=f""" Rewrite the query for document retrieval.

Rules:
1. Keep important keywords.
2. Keep technical terms.
3. Do not make the query longer than necessary.
4. Preserve the original meaning.

Question:
{question}

Return only the rewritten query.
    """
        response=model.generate_content(prompt)
        return response.text.strip()
    
    def rewrite(state):
        question =state["question"]
        rewritten=rewrite_query(question)
        return { "rewritten_query": rewritten}
    
    # contextual compression
    def compress_docs(question, docs):
     combined_context="\n\n".join(doc.page_content for doc in docs)
     
     prompt = f"""
        Extract only the information
        relevant to the question.

        Question:
        {question}

        Context:
        {combined_context}

        Return only relevant content.
        """
     response = model.generate_content(prompt)
     return [response.text]
    
    # node 1
    def retrieve(state):
        selected_pdf=state['selected_pdf']
        question = state["rewritten_query"]
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
        if not unique_docs:
            return {
                'documents':[],
                'rerank_scores':[],
                'top_score':0.0
            }  
        if selected_pdf!='All PDFs':
            filtered_by_pdf=[]
            for doc in unique_docs:
                source=doc.metadata.get('source',"")
                if selected_pdf in source:
                    filtered_by_pdf.append(doc)
            unique_docs=filtered_by_pdf
                
            # filter useless chunks
        filtered_docs=[]
        for doc in unique_docs:
            text=doc.page_content.strip()
            if len(text)<30:
                continue
            if any(keyword in text.lower() for keyword in [ 
        "thank you",
        "references",
        "acknowledgement",
        "acknowledgements",
        "submitted by",
        "mini-project",
        "course",
        "roll no",
        "university",
        "names"
            ]):
                continue
            filtered_docs.append(doc)
        unique_docs=filtered_docs
                
        # reranking 
        pairs =[(question,doc.page_content)
                for doc in unique_docs]
        # safety check
        if not pairs:
            return {
                'documents':[],
                'rerank_scores':[],
                'top_score':0.0
            }
        scores=reranker.predict(pairs)
        ranked_docs=sorted(zip(unique_docs,scores),key=lambda x: x[1],reverse=True) 
        if ranked_docs:
            top_score = float(ranked_docs[0][1])
            max_score = ranked_docs[0][1]
            min_score = ranked_docs[-1][1]
        else:
            top_score = 0.0
            max_score=0.0 
            min_score = 0.0
        rerank_scores = []
        for doc, score in ranked_docs:
            if max_score != min_score:
                relative_score = (
                (score - min_score) / (max_score - min_score)
        ) * 100
            else:
                relative_score = 100
            rerank_scores.append({
        "score": float(score),
        "relative_score": float(relative_score),
        "content": doc.page_content[:200]
    })
        top_docs=[doc for doc,score in ranked_docs[:3]]
        return {
     "documents": top_docs,
    "rerank_scores": rerank_scores,
    "top_score": top_score
         }
        # create compression node
        
    def compress(state):
        question =state['question']
        docs =state['documents']
        compressed_docs=compress_docs(question,docs)
        return {
            'compressed_docs':compressed_docs
        }
    # NODE 2
   

    def decide(state):
        docs=state.get('documents',[])
        if docs:
            return 'answer'
        return 'web_search'

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
        docs = state.get("compressed_docs", [])
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
    workflow.add_node('rewrite',rewrite)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("web_search", web_search)
    workflow.add_node('compress',compress)
    workflow.add_node("answer", generate_answer)

    workflow.set_entry_point("rewrite")



    workflow.add_conditional_edges(

        "retrieve",
        decide,

        {

            "answer": "compress",

            "web_search": "web_search"
        }
    )

    workflow.add_edge('rewrite','retrieve')
    workflow.add_edge('compress','answer')
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
                    "question": question,
                    "selected_pdf": selected_pdf
                }
            )

        # ANSWER

        st.subheader("🤖 AI Answer")
        st.markdown(response["answer"])
        st.subheader(" Rewritten Query")
        st.write(response['rewritten_query'])
        st.subheader("  Reranker Scores")
        rank=1
        for item in response['rerank_scores']:
           st.write( f"Rank {rank} | Relevance: {item['relative_score']:.1f}%")
           st.write(f"Content: {item['content']}")
           st.divider()
           rank+=1
        # DOCS
        st.subheader("📄 Retrieved Chunks")

        for i, doc in enumerate(response["documents"]):

          if len(doc.page_content.strip()) > 50:

           with st.expander(f"Chunk {i+1}"):

            st.markdown(
                f"""
📃 Source: {doc.metadata.get('source','Unknown')}

📄 Page: {doc.metadata.get('page','Unknown')}

📝 Content:

{doc.page_content}
"""
            )
        st.subheader('Compressed context')
        for doc in response['compressed_docs']:
            st.write(doc)

        # WEB SEARCH

        if response.get("web_search"):

           with st.subheader("🌐 Web Search Results"):

            st.write(response["web_search"])
        