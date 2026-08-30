from typing import TypedDict,Any,List

class AgentState(TypedDict,total=False):
    # user input
    question:str
    selected_file:str
    
    #Search query used by retrieval
    search_query:str
    previous_query:str
    
    # retrieval
    retrieved_docs:List[Any]
    ranked_docs:List[Any]
    graph_results:List[Any]
    
    # context
    context:str
    top_docs:List[Any]
    
    #Conversation
    history:str
    
    # generation
    answer:str
    
    #Evaluation
    confidence:str
    decision:str
    
    # control
    retry_count:int
    search_query:str
    previous_query:str