from app.core.logger import logger
from app.services.retrieval_service import retrieval_service
from app.services.reranker_service import reranker_service
from app.services.context_builder import context_builder_service
from app.services.generation_service import generation_service
from app.services.memory_service import memory_service
from app.core.gemini_utils import log_gemini_error
from app.services.graph_retrieval_service import graph_retrieval_service
from app.core.config import model
import re


def retrieve_node(state):
    logger.info("Agent node: retrieval started")

    question = state["question"]
    search_query=state.get('search_query',question)
    
    selected_file = state.get(
        "selected_file",
        "All Files"
    )
    logger.info(f'Agent search query: {search_query}')

    docs = retrieval_service.retrieval(
        search_query,
        selected_file
    )

    logger.info(
        f"Agent retrieval returned {len(docs)} documents"
    )

    return {
        "retrieved_docs": docs
    }

def graph_retrieval_node(state):
    logger.info('Agent node: graph retrieval started')
    question=state.get('question',"")
    graph_results=graph_retrieval_service.retrieve(question)
    logger.info(f'Agent graph retrieval returned'
                f"{len(graph_results)} relationships")
    
    return{'graph_results':graph_results}

def rerank_node(state):
    logger.info("Agent node: reranking started")

    question = state["question"]

    docs = state.get(
        "retrieved_docs",
        []
    )

    if not docs:
        logger.warning(
            "No documents available for reranking"
        )

        return {
            "ranked_docs": []
        }

    ranked_docs = reranker_service.rerank(
        question,
        docs
    )

    logger.info(
        f"Agent reranking returned "
        f"{len(ranked_docs)} documents"
    )

    return {
        "ranked_docs": ranked_docs
    }


def context_node(state):
    logger.info("Agent node: context building started")

    ranked_docs = state.get(
        "ranked_docs",
        []
    )
    graph_results=state.get('graph_results',[])
    context=""
    top_docs=[]
    
    if ranked_docs:

        context, top_docs = (
            context_builder_service.build_context(
                ranked_docs
            )
        )

    else:

        logger.warning(
            "No ranked documents available"
        )
    
    combined_context=context
    if graph_results:
        graph_lines=[]
        
        for edge in graph_results:
            graph_lines.append(f"{edge['source']}"
                               f"--[{edge['relationship']}]-->"
                               f"{edge['target']}")
            
            graph_context="\n".join(graph_lines)
        
        if combined_context:
            combined_context+=("\n\nGRAPH CONTEXT:\n"+graph_context)  
        else:
            combined_context=('GRAPH CONTEXT:\n'+graph_context) 
                     
    logger.info(
        f"Agent context contains "
        f"{len(top_docs)} documents and"
        f"{len(graph_results)} graph relationships"
    )

    return {
        "context": combined_context,
        "top_docs": top_docs
    }
    
def generation_node(state):
    logger.info('Agent node: generation started')
    
    question=state['question'] 
    context=state.get('context',"")
    
    history=memory_service.build_history()
    if not context:
        logger.warning('No context available for generation') 
        return {'answer':( "I couldn't find this information "
                "in the uploaded PDF(s)."),'history':history} 
        
    answer=generation_service.generate(question,context,history)
    logger.info('Agent answer generated successfully') 
    
    return {'answer':answer,
            'history':history}
    
def evaluate_context_node(state):
    """
    Generic deterministic context evaluator.

    Works with:
    - documents
    - websites
    - YouTube/video transcripts
    - audio transcripts
    - OCR/image text
    - any source that produces textual context

    The evaluator does NOT depend on specific topics, domains,
    entities, file types, or hard-coded keywords.
    """

    question = state.get("question", "").strip()
    context = state.get("context", "").strip()
    retry_count = state.get("retry_count", 0)
    graph_results = state.get("graph_results", [])

    # 1. Maximum retry protection
    if retry_count >= 2:
        logger.warning(
            "Maximum retries reached - context remains insufficient"
        )

        return {
            "decision": "insufficient",
            "retry_count": retry_count
        }

    # 2. Empty question / empty context
    
    if not question:
        logger.warning("Empty question")
        return {
            "decision": "insufficient",
            "retry_count": retry_count
        }

    if not context:
        logger.warning("Empty context")
        return {
            "decision": "retry",
            "retry_count": retry_count + 1
        }

    # 3. Normalize text

    question_normalized = question.lower()
    context_normalized = context.lower()

    question_tokens = re.findall(
        r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
        question_normalized
    )

    context_tokens = set(
        re.findall(
            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
            context_normalized
        )
    )

    if not question_tokens:
        return {
            "decision": "insufficient",
            "retry_count": retry_count
        }

    # ---------------------------------------------------------
    # 4. Stop words
    #
    # These are generic language words, not domain-specific
    # words.
    # ---------------------------------------------------------

    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "am",
        "do",
        "does",
        "did",
        "doing",
        "have",
        "has",
        "had",
        "having",
        "can",
        "could",
        "will",
        "would",
        "shall",
        "should",
        "may",
        "might",
        "must",
        "of",
        "to",
        "for",
        "from",
        "in",
        "on",
        "at",
        "by",
        "with",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "over",
        "and",
        "or",
        "but",
        "if",
        "then",
        "than",
        "as",
        "so",
        "because",
        "while",
        "where",
        "when",
        "how",
        "why",
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "they",
        "them",
        "their",
        "there",
        "here",
        "you",
        "your",
        "we",
        "our",
        "i",
        "me",
        "my",
        "he",
        "she",
        "his",
        "her",
        "not",
        "no",
        "yes",
        "tell",
        "explain",
        "describe",
        "give",
        "show",
        "mean",
        "means",
        "used",
        "use",
    }

    # 5. Extract meaningful question terms
   
    meaningful_tokens = [
        token
        for token in question_tokens
        if token not in stop_words
        and len(token) > 1
    ]

    meaningful_tokens = set(meaningful_tokens)

    logger.info(
        f"Content-bearing question words: {meaningful_tokens}"
    )


    overlap = meaningful_tokens.intersection(context_tokens)
    logger.info(
        f"Content-bearing overlap count: {len(overlap)}" )

    relationship_patterns = [
        r"\brelationship between\b",
        r"\brelationship of\b",
        r"\brelationship with\b",
        r"\bconnection between\b",
        r"\bconnection with\b",
        r"\bconnected to\b",
        r"\brelated to\b",
        r"\bassociation between\b",
        r"\bassociated with\b",
        r"\blink between\b",
        r"\blinked to\b",
        r"\bhow .* related\b",
        r"\bhow .* connected\b",
    ]

    question_has_relationship = any(
        re.search(pattern, question_normalized)
        for pattern in relationship_patterns
    )

    if question_has_relationship:
        logger.info(
            "Explicit relationship intent detected"
        )

        if graph_results:
            logger.info(
                f"Graph evidence available: "
                f"{len(graph_results)} relationships"
            )

            return {
                "decision": "generate",
                "retry_count": retry_count
            }

        if len(overlap) >= 2:
            logger.info(
                "No graph evidence, but textual context "
                "contains sufficient relevant terms" )

            return {
                "decision": "generate",
                "retry_count": retry_count
            }

        logger.warning(
            "Relationship question has insufficient evidence"
        )
        return {
            "decision": "retry",
            "retry_count": retry_count + 1
        }
        
    if len(overlap) >= 2:

        logger.info(
            "Sufficient lexical grounding detected" )

        return {
            "decision": "generate",
            "retry_count": retry_count
        }

    if len(meaningful_tokens) == 1 and len(overlap) == 1:

        logger.info(
            "Short factual question has direct context match"
        )

        return {
            "decision": "generate",
            "retry_count": retry_count
        }

    if len(overlap) == 1 and graph_results:

        logger.info(
            "Single-term question supported by graph evidence"
        )

        return {
            "decision": "generate",
            "retry_count": retry_count
        }

    logger.warning(
        "Retrieved context does not contain sufficient "
        "evidence for the question"
    )

    return {
        "decision": "retry",
        "retry_count": retry_count + 1
    }
    
def refine_query_node(state):
    logger.info('Agent node: query refinement started')
    question=state.get('question',"")
    
    current_query=state.get('search_query',question)  
    previous_query=state.get('previous_query',"") 
    retry_count=state.get('retry_count',0)
    
    if retry_count>1:
        logger.warning('Query refinement limit reached')
        return {'search_query':current_query}
    
    if previous_query==current_query:
        logger.warning('Query has already been refined.'
                       'Skipping another refinement')
        return {'search_query':current_query}
    
    refinement_prompt = f"""
You are a query refinement component for an AI Research Assistant.

The user asked:

{question}

The current search query is:

{current_query}


The retrieved context was judged irrelevant or insufficient.

Create a better search query that can retrieve information
from the uploaded documents that is relevant to the user's question.

Rules:

1. Keep the meaning of the user's question.
2. Use important keywords from the question.
3. Make the query more specific if necessary.
4. Do not answer the question.
5. Do not add facts that are not present in the user's question.
6. Return ONLY the improved search query.
"""
    try:

        logger.info(
            'Query refinement Gemini call started'
        )
        response = model.generate_content(
            refinement_prompt
        )
        refined_query = response.text.strip()

        if not refined_query:
            logger.warning(
                'Empty refined query'
            )
            return {
                'search_query': current_query
            }

        if refined_query == current_query:
            logger.info(
                'Refined query unchanged'
            )
            return {
                'search_query': current_query,
                'previous_query': current_query
            }

        logger.info(
            f'Refined search query: '
            f'{refined_query}'
        )
        return {
            'search_query': refined_query,
            'previous_query': current_query
        }

    except Exception as e:

        log_gemini_error(
            'query refinement',
            e
        )
        return {
            'search_query': current_query,
            'previous_query': current_query
        }
     
 
def insufficient_context_node(state):
    logger.warning('Unable to find sufficient relevant context')
    
    return {
        'answer':("I couldn't find this information" 
                  "in the uploaded document(s).")
    }    
    
    