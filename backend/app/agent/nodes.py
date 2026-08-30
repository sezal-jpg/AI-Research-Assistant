from app.core.logger import logger
from app.services.retrieval_service import retrieval_service
from app.services.reranker_service import reranker_service
from app.services.context_builder import context_builder_service
from app.services.generation_service import generation_service
from app.services.memory_service import memory_service
from app.core.gemini_utils import log_gemini_error
from app.services.graph_retrieval_service import graph_retrieval_service
from app.core.config import model


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
        logger.warning('No ranked documents available')    
        
    graph_context=""
    if graph_results:
        graph_lines=[]
        
        for edge in graph_results:
            graph_lines.append(f"{edge['source']}"
                               f"--[{edge['relationship']}]-->"
                               f"{edge['target']}")
            
            graph_context="\n".join(graph_lines)
            
    combined_context=context
    if graph_context:        
        
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

    logger.info('Agent node: evaluating context')
    question = state.get(
        'question',
        ''
    )
    context = state.get(
        'context',
        ''
    )
    retry_count = state.get(
        'retry_count',
        0
    )
    logger.info(
        f'Current retry count : {retry_count}'
    )

    if retry_count >= 2:
        logger.warning(
            'Maximum retries reached - '
            'context remains insufficient'
        )
        return {
            'decision': 'insufficient'
        }

    if not context.strip():
        logger.warning(
            'No context available'
        )
        return {
            'decision': 'retry',
            'retry_count': retry_count + 1
        }

    question_words = {
        word.lower().strip(".,?!:;()[]{}")
        for word in question.split()
        if len(
            word.strip(".,?!:;()[]{}")
        ) > 3
    }

    context_words = {
        word.lower().strip(".,?!:;()[]{}")
        for word in context.split()
        if len(
            word.strip(".,?!:;()[]{}")
        ) > 3
    }

    overlap = question_words.intersection(
        context_words
    )
    logger.info(
        f'Keyword overlap count: {len(overlap)}'
    )

    if not overlap:
        logger.warning(
            'No meaningful keyword overlap found '
            'between question and context'
        )
        return {
            'decision': 'retry',
            'retry_count': retry_count + 1
        }
    
    evaluation_prompt = f"""
You are a strict context evaluator for an AI Research Assistant.

Your task is to determine whether the retrieved context contains
enough relevant information to answer the user's question.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Rules:

1. The context must be relevant to the question.
2. Do not use your own knowledge.
3. Do not assume missing information.
4. If the context is unrelated or insufficient, return NO.
5. If the context directly contains enough information to answer
   the question, return YES.

Return ONLY one word:

YES

or

NO
"""
    try:    
     response=model.generate_content(evaluation_prompt)
     decision_result=response.text.strip().upper()
     logger.info(f'Context evaluator result: {decision_result}')

     if decision_result=='YES':
      logger.info('Context is relevant and sufficient')
      return {'decision':'generate'}
    
     logger.warning('context is irrelevant or insufficient')
    
     return {'decision':'retry',
            'retry_count':retry_count+1}
     
    except Exception as e:
       error_type=log_gemini_error('context evaluation',e)
       if error_type=='quota':
           logger.warning('Context evaluation unavailable'
                          'because Gemini quota is exhausted')
           return {'decision':'insufficient'}
       
       return {'decision':'retry',
               'retry_count':retry_count+1}
           
    
def refine_query_node(state):
    logger.info('Agent node: query refinement started')
    question=state.get('question',"")
    
    current_query=state.get('search_query',question) 
    context=state.get('context',"")  
    previous_query=state.get('previous_query',"") 
    
    if previous_query==current_query:
        logger.warning('Query has already been refined.'
                       'Skipping another refinement')
        return {'search_query':current_query,
                'previous_query':current_query}
    
    refinement_prompt = f"""
You are a query refinement component for an AI Research Assistant.

The user asked:

{question}

The current search query is:

{current_query}

The retrieved context was:

{context}

The context was judged irrelevant or insufficient.

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
     response=model.generate_content(refinement_prompt)   
     refined_query=response.text.strip()
    
     if not refined_query:
        logger.warning('Query refinement produced an empty query')
        refined_query=current_query
        
     if refined_query==current_query:
        logger.info('Refined query is unchanged')
        return {'search_query':current_query,
                'previous_query':current_query}    
        
     logger.info(f'Refined search query: {refined_query}')
     return {'search_query': refined_query,
            'previous_query':current_query}  
    
    except Exception as e:
     log_gemini_error('query refinement',e)
     return {'search_query':current_query,
             'previous_query':current_query}
     
 
def insufficient_context_node(state):
    logger.warning('Unable to find sufficient relevant context')
    
    return {
        'answer':("I couldn't find this information" 
                  "in the uploaded document(s).")
    }    
    
    