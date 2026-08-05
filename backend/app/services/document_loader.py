from pathlib import Path
from langchain_community.document_loaders import(PyPDFLoader,TextLoader,UnstructuredWordDocumentLoader,UnstructuredPowerPointLoader,)
class DocumentLoader:
    def load(self,file_path:Path):
        suffix=file_path.suffix.lower()
        if suffix==".pdf":
            loader=PyPDFLoader(str(file_path))
        elif suffix=='.docx':
            loader=UnstructuredWordDocumentLoader(str(file_path))    
        elif suffix=='.pptx':
            loader=UnstructuredWordDocumentLoader(str(file_path)) 
        elif suffix=='.txt':
            loader=TextLoader(str(file_path),encoding='utf-8')
        elif suffix =='.md':
            loader=TextLoader(str(file_path),encoding='utf-8')  
        else:
            raise ValueError(
                f'unsupported file type: {suffix}'
            ) 
        return loader.load()
document_loader=DocumentLoader()                 