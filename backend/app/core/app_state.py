class AppState:
    def __init__(self):
        self.vectorstore=None
        self.bm25_retriever=None
        self.all_chunks=[]
        self.conversation_history=[]
state=AppState()        