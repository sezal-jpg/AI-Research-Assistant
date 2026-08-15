from pathlib import Path
import pandas as pd
from langchain_core.documents import Document
from app.core.logger import logger

class CsvLoader:
 def load(self,file_path:Path):
        
    logger.info(f'Loading CSV: {file_path.name}')
    dataframe=pd.read_csv(file_path)
     
    if dataframe.empty:
         logger.warning(f'CSV is empty: {file_path.name}')
         return []
    docs=[]
    batch_size=100
    for start in range(0,len(dataframe),batch_size):
         batch=dataframe.iloc[start:start+batch_size]
         content=batch.to_string(index=False)
     
         if content.strip():
          docs.append(Document(page_content=content,metadata={'source_file':file_path.name,'source_type':'csv','row_start':start+1,'row_end':min(start+batch_size,len(dataframe),)}))
    logger.info(f'CSV rows" {len(dataframe)}')
    logger.info(f'created {len(docs)} CSV document batches')
    return docs
     
 
csv_loader=CsvLoader() 