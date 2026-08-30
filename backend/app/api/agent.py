from fastapi import APIRouter
from app.agent.graph import agent_graph

router=APIRouter(prefix='/agent',tags=['Agent'])
@router.post('/ask')
def agent_ask(question:str,selected_file:str='All Files'):
    
    result=agent_graph.invoke({'question':question,'selected_file':selected_file,'search_query':question,'retry_count':0})
    return {
        'question':result.get('question'),
        'answer':result.get('answer',""),
        'retrieved_documents':len(result.get('retrieved_docs',[])),
        'ranked_documents':len(result.get('ranked_docs',[])),
        'top_documents':len(result.get('top_docs',[])),
        'context':result.get('context',"")
}
    
    