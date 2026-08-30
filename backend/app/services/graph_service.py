from app.core.logger import logger

class GraphService:
    def __init__(self):
        self.edges=[]
        self.nodes={}
        logger.info('Graph Service initialized')
        
    def add_node(self,node_id,node_type,properties=None):
        
        if properties is None:
            properties={}
          
        if node_id not in self.nodes:    
            
         self.nodes[node_id]={
            'id':node_id,
            'type':node_type,
            'properties':properties
        }   
         logger.info(f'Graph node added: {node_id}')
        
    def add_edge(self,source,relationship,target):
        edge={'source':source,
              'relationship':relationship,
              'target':target}
        
        if edge not in self.edges:
         self.edges.append(edge)
         logger.info(f'Graph edge added:'
                    f'{source}-[{relationship}]->{target}')
        
    def add_entities(self,entities):
        
        for entity in entities:
            name=entity.get('name')
            entity_type=entity.get('type','concept')    
            
            if name:
                self.add_node(node_id=name,node_type=entity_type)
                
    def add_relationships(self,relationships):
        for relationship in relationships:
            source=relationship.get('source')
            relation=relationship.get('relationship')
            target=relationship.get('target')
            
            if source and relation and target:
                self.add_edge(source,relation,target)
                            
    def get_node(self,node_id):
        return self.nodes.get(node_id)
    
    def get_edges(self):
        return self.edges
    
    def get_nodes(self):
        return list(self.nodes.values())
    
    def search(self,query):
        query=query.lower().strip()
        if not query:
            return []
        
        results=[]
        
        matched_nodes=set()
        for node_id,node in self.nodes.items():
            if query in node_id.lower():
                matched_nodes.append(node_id)
                
        for edge in self.edges:
            if(edge['source'] in matched_nodes or edge['target'] in matched_nodes):
                results.append(edge)
                
        logger.info(f'Graph search found'
                f"{len(results)} relationships")     
        return results    

graph_service=GraphService()                
        