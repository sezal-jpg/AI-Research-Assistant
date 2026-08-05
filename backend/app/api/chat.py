from fastapi import APIRouter
from app.models.chat import QuestionRequest
from app.services.chat_service import chat_service
router=APIRouter(prefix="",tags=['Chat'])
@router.post('/ask')
def ask(request:QuestionRequest):
    return chat_service.ask(request)