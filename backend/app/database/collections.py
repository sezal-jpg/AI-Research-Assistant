import json
import os
class CollectionManager:
    def __init__(self):
        self.db_path='data/collections.json'
    def load(self):
        if not os.path.exists(self.db_path):
            return []
        with open(self.db_path,'r') as f:
            return json.load(f)    
    def save(self,collections):
        with open(self.db_path,'w') as f:
            json.dump(collections,f,indent=4)
    def list_collections(self):
        return self.load()       
collection_manager=CollectionManager() 
                