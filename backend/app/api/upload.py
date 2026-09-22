from typing import List
from fastapi import APIRouter,UploadFile,File,HTTPException
from app.services.ingestion_service import ingestion_service
from app.core.app_state import state
from app.core.logger import logger

router=APIRouter(prefix="",tags=['Uploaded'])

@router.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        return await ingestion_service.process_documents(files)

    except ValueError as e:
        logger.warning(
            f"Upload blocked: {e}" )
        
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        logger.error(
            f"File processing failed: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="The uploaded file could not be processed."
        )

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



