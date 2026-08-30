class AppState:
    def __init__(self):
        self.all_chunks=[]
        self.parent_chunks={}
        self.vectorstore=None
        self.bm25_retriever=None
        self.clip_embeddings={}
        self.conversation_history=[]
        
state=AppState()        