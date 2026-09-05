import json
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from app.core.app_state import state
from app.core.logger import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.loader_factory import loader_factory
from app.services.graph_construction_service import graph_construction_service
from app.services.embedding_service import get_embedding_model
from app.services.graph_service import graph_service

class PersistenceService:
    
    def __init__(self):
        self.db_dir=Path('db')
        self.data_dir=Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.chunks_file=self.data_dir/'indexed_chunks.json'
        self.graph_file=self.data_dir/'graph.json'
        self.embedding_model=(get_embedding_model())
        
    def restore_parent_chunks(self):
     if state.parent_chunks:
        logger.info(
            'Parent chunks already restored'
        )
        return

     upload_dir = Path('uploads')

     if not upload_dir.exists():
        logger.warning(
            'Uploads directory not found'
        )
        return

     parent_splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150
        )
    )

     restored_count = 0
     for file_path in upload_dir.iterdir():

        if not file_path.is_file():
            continue

        try:
            loader = (
                loader_factory.get_loader(
                    file_path))

            if loader is None:
                logger.warning(
                    f'No loader for '
                    f'{file_path.name}')
                continue

            docs = loader.load(file_path)
            for doc in docs:
                doc.metadata[
                    'source_file'
                ] = file_path.name

            parent_chunks = (
                parent_splitter.split_documents( docs  ))

            for parent_index, parent in enumerate(  parent_chunks ):
                parent_id = (
                    f"{file_path.name}_"
                    f"{parent_index}"
                )

                parent.metadata[
                    'parent_id'
                ] = parent_id

                parent.metadata[
                    'chunk_type'
                ] = 'parent'

                state.parent_chunks[
                    parent_id
                ] = parent
                restored_count += 1

        except Exception as e:
            logger.error(
                f'Failed to restore parents '
                f'from {file_path.name}: {e}'
            )
     logger.info(
        f'Restored {restored_count} '
        'parent chunks'
    )    
        
    def save_chunks(self):
     chunks_data = {
        'parents': [],
        'children': []
    }

     for parent_id, parent in state.parent_chunks.items():
        chunks_data['parents'].append({
            'parent_id': parent_id,
            'page_content': parent.page_content,
            'metadata': parent.metadata
        })

     for chunk in state.all_chunks:
        chunks_data['children'].append({
            'page_content': chunk.page_content,
            'metadata': chunk.metadata
        })

     with open(
        self.chunks_file,
        'w',
        encoding='utf-8'
    ) as file:
        json.dump(
            chunks_data,
            file,
            ensure_ascii=False,
            indent=2
        )

     logger.info(
        f"Saved {len(chunks_data['parents'])} parents "
        f"and {len(chunks_data['children'])} children"
    )
        
    def load_chunks(self):
     if not self.chunks_file.exists():
        logger.info('No persisted chunks found')
        return

     with open(
        self.chunks_file,
        'r',
        encoding='utf-8'
    ) as file:
        chunks_data = json.load(file)

     state.all_chunks = []
     state.parent_chunks = {}

     for item in chunks_data.get('parents', []):

        document = Document(
            page_content=item['page_content'],
            metadata=item['metadata']
        )
        parent_id = item.get('parent_id')

        if parent_id:
            state.parent_chunks[parent_id] = document

     for item in chunks_data.get('children', []):
        document = Document(
            page_content=item['page_content'],
            metadata=item['metadata']
        )
        state.all_chunks.append(document)

     logger.info(
        f"Loaded {len(state.parent_chunks)} parents "
        f"and {len(state.all_chunks)} children "
        f"from persistence"
    )  
     
    def restore_chunks_from_chroma(self):
     if state.all_chunks:
        logger.info(
            'Chunk metadata already restored'
        )
        return

     if state.vectorstore is None:
        logger.warning(
            'Cannot restore chunks: '
            'vectorstore unavailable'
        )
        return

     try:
        result = state.vectorstore.get(
            include=[
                'documents',
                'metadatas'
            ]
        )
        documents = result.get(
            'documents',
            []
        )
        metadatas = result.get(
            'metadatas',
            []
        )

        for text, metadata in zip(
            documents,
            metadatas
        ):
            if not text:
                continue

            document = Document(
                page_content=text,
                metadata=metadata or {}
            )
            state.all_chunks.append(
                document
            )
        logger.info(
            f"Restored {len(state.all_chunks)} "
            'child chunks from Chroma'
        )

     except Exception as e:
        logger.error(
            f'Failed to restore chunks '
            f'from Chroma: {e}'
        )   
     
    def restore_vectorstore(self):
        if not self.db_dir.exists():
            logger.info('No Chroma database found')
            return 
        
        try:
            state.vectorstore=Chroma(persist_directory=str(self.db_dir),embedding_function=(self.embedding_model))
            
            logger.info('chroma vector store restored')  
            
        except Exception as e:
            logger.error(f'Failed to restore chroma: {e}')      
            state.vectorstore=None
            
    def restore_bm25(self):
        if not state.all_chunks:
            logger.info('No chunks available' 'for bm25 restoration') 
            return  
        
        state.bm25_retriever=(BM25Retriever.from_documents(state.all_chunks))                  
        state.bm25_retriever.k=3
        logger.info('BM25 retriever resotred')
        
    def save_graph(self):
        graph_data={'nodes':graph_service.get_nodes(),
                    'edges':graph_service.get_edges(),
                    'processed_chunks':list(graph_construction_service.processed_chunks)}   
        
        with open(self.graph_file,'w',encoding='utf-8') as file:
            json.dump(graph_data,file,ensure_ascii=False,indent=2) 
            
        logger.info(
            f"Saved graph: "
            f"{len(graph_data['nodes'])} nodes, "
            f"{len(graph_data['edges'])} edges"
        )
        
    def load_graph(self):
        if not self.graph_file.exists():
            logger.info('No persisted graph found')
            return 
        
        with open(self.graph_file,'r',encoding='utf-8')as file:
            graph_data=json.load(file)
        graph_service.nodes={}
        graph_service.edges=[]
        
        for node in graph_data.get('nodes',[]):
             graph_service.add_node(node_id=node['id'],
                                    node_type=node['type'],
                                    properties=node.get('properties',{}))    
        for edge in graph_data.get('edges',[]):
            graph_service.add_edge(source=edge['source'],
            relationship=edge['relationship'],
            target=edge['target'] ) 
        
        graph_construction_service.processed_chunks=set(graph_data.get('processed_chunks',[]))    
            
        logger.info(f'Graph restored:'
                    f"{len(graph_service.nodes)} nodes"
                    f" {len(graph_service.edges)} edges")
        
    def restore_all(self):
        logger.info('Starting persistent state restoration')
        
        self.restore_vectorstore() 
        self.load_chunks()
        self.restore_chunks_from_chroma()
        self.restore_parent_chunks()
        self.restore_bm25()
        self.load_graph()  
        logger.info('Persistent state restoration completed')
        
persistence_service=PersistenceService()                  