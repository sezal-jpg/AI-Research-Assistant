from langgraph.graph import StateGraph,START,END
from app.agent.state import AgentState
from app.core.logger import logger
from app.agent.nodes import (retrieve_node,rerank_node,context_node,generation_node,evaluate_context_node,refine_query_node,insufficient_context_node)

def route_after_evaluation(state):
    decision=state.get('decision','insufficient')
    logger.info(f'Agent decision: {decision}')
    return decision

graph_builder=StateGraph(AgentState)

graph_builder.add_node('retrieve',retrieve_node)
graph_builder.add_node('rerank',rerank_node)
graph_builder.add_node('context',context_node)
graph_builder.add_node('evaluate',evaluate_context_node)
graph_builder.add_node('refine',refine_query_node)
graph_builder.add_node('generate',generation_node)
graph_builder.add_node('insufficient',insufficient_context_node)

graph_builder.add_edge(START,'retrieve')
graph_builder.add_edge('retrieve','rerank')
graph_builder.add_edge('rerank','context')
graph_builder.add_edge('context','evaluate')



graph_builder.add_conditional_edges(
    "evaluate",
    route_after_evaluation,
    {
        "generate": "generate",
        "retry": "refine",
        'insufficient':'insufficient'
    }
)

graph_builder.add_edge('refine','retrieve')
graph_builder.add_edge('generate',END)
graph_builder.add_edge('insufficient',END)

agent_graph=graph_builder.compile()
