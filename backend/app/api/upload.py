from typing import List
from fastapi import APIRouter,UploadFile,File
from app.services.ingestion_service import ingestion_service
from app.core.app_state import state

router=APIRouter(prefix="",tags=['Uploaded'])

@router.post("/upload")
async def upload_pdfs(files: List[UploadFile]=File(...)):
    return await ingestion_service.process_documents(files)

@router.get("/sources")
async def get_sources():
    sources=set()
    for chunk in state.all_chunks:
         source=chunk.metadata.get('source_file')
         
         if source:
             sources.add(source)
             
    return {
        'sources':sorted(sources)
    }         



