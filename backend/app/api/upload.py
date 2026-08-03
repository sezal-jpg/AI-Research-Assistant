from typing import List
from fastapi import APIRouter,UploadFile,File
from app.services.ingestion_service import ingestion_service
router=APIRouter(prefix="",tags=['Uploaded'])
@router.post("/upload")
async def upload_pdfs(files: List[UploadFile]=File(...)):
    return await ingestion_service.process_documents(files)




