from app.core.app_state import state
from app.core.logger import logger
from langchain_community.retrievers import BM25Retriever


class RetrievalService:

    def retrieval(self, question, selected_file):

        if state.vectorstore is None or state.bm25_retriever is None:
            logger.warning(
                "Vectorstore or BM25 retriever is not initialized"
            )
            return []

        logger.info(
            f"Retrieving for question: {question}"
        )

        logger.info(
            f"Selected source: {selected_file}"
        )

        # ALL FILES
    

        if selected_file == "All Files":

            semantic_docs = state.vectorstore.similarity_search(
                question,
                k=8
            )

            bm25_docs = state.bm25_retriever.invoke(
                question
            )
            
           # YouTube Source
        elif selected_file.startswith( "https://www.youtube.com/") or selected_file.startswith("https://youtu.be/"):
            semantic_docs=(state.vectorstore.similarity_search(question,k=8,filter={'source_url':selected_file}))
            filtered_chunks=[chunk for chunk in state.all_chunks
                             if chunk.metadata.get('source_url')==selected_file]
            
            if not filtered_chunks:
                logger.warning(f'No chunks found for youtube:' f'{selected_file}')
                return []
            
            filtered_bm25=(BM25Retriever.from_documents(filtered_chunks))
            filtered_bm25.k=8
            bm25_docs=(filtered_bm25.invoke(question))
            
               

        else:

            # -------------------------------------------------
            # Check whether selected source is a website
            # -------------------------------------------------

            website_chunks = [
                chunk
                for chunk in state.all_chunks
                if chunk.metadata.get("source_url") == selected_file
            ]

            # -------------------------------------------------
            # WEBSITE
            # -------------------------------------------------

            if website_chunks:

                logger.info(
                    f"Website source selected: {selected_file}"
                )

                semantic_docs = state.vectorstore.similarity_search(
                    question,
                    k=8,
                    filter={
                        "source_url": selected_file
                    }
                )

                filtered_bm25 = BM25Retriever.from_documents(
                    website_chunks
                )

                filtered_bm25.k = 8

                bm25_docs = filtered_bm25.invoke(
                    question
                )

            # -------------------------------------------------
            # PDF / IMAGE / FILE
            # -------------------------------------------------

            else:

                logger.info(
                    f"File source selected: {selected_file}"
                )

                semantic_docs = state.vectorstore.similarity_search(
                    question,
                    k=8,
                    filter={
                        "source_file": selected_file
                    }
                )

                filtered_chunks = [
                    chunk
                    for chunk in state.all_chunks
                    if chunk.metadata.get("source_file") == selected_file
                ]

                if not filtered_chunks:

                    logger.warning(
                        f"No chunks found for {selected_file}"
                    )

                    return []

                filtered_bm25 = BM25Retriever.from_documents(
                    filtered_chunks
                )

                filtered_bm25.k = 8

                bm25_docs = filtered_bm25.invoke(
                    question
                )

        # =====================================================
        # LOG RETRIEVAL RESULTS
        # =====================================================

        logger.info(
            f"Semantic results: {len(semantic_docs)}"
        )

        logger.info(
            f"BM25 results: {len(bm25_docs)}"
        )

        # RECIPROCAL RANK FUSION(RRF)

        rrf_scores={}
        doc_map={}
        
        rrf_k=60

        # SEmantic Search Ranking
        
        for rank,doc in enumerate(semantic_docs,start=1):
            content=doc.page_content.strip()
            
            if not content:
                continue
            
            if content not in doc_map:
                doc_map[content]=doc
                
            rrf_scores[content]=(rrf_scores.get(content,0)+1/(rrf_k+rank)) 
            
            # BM25 Ranking
            
        for rank,doc in enumerate(bm25_docs,start=1): 
            content=doc.page_content.strip()
            
            if not content:
                continue
            
            if content not in doc_map:
                doc_map[content]=doc
                
            rrf_scores[content]=(rrf_scores.get(content,0)+1/(rrf_k+rank))     
            
            # Sort by rrf score
            
        ranked_contents=sorted(rrf_scores,key=rrf_scores.get,reverse=True)
        
        unique_docs=[doc_map[content] for content in ranked_contents]   
        logger.info(f'Hybrid RRF results: {len(unique_docs)}')  
               

        # =====================================================
        # LOG SOURCES
        # =====================================================

        for index, doc in enumerate(unique_docs):

            source_file = doc.metadata.get(
                "source_file"
            )

            source_url = doc.metadata.get(
                "source_url"
            )

            logger.info(
                f"Result {index + 1}: "
                f"file={source_file}, "
                f"url={source_url}"
            )

        return unique_docs


retrieval_service = RetrievalService()