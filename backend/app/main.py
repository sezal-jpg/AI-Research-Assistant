from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.website import router as website_router
from app.api.audio import router as audio_router
from app.api.tts import router as tts_router
from app.api.youtube import router as youtube_router
from app.api.agent import router as agent_router
from app.core.exceptions import(AppException,app_exception_handler,generic_exception_handler,)

app=FastAPI(title='OmniResearch AI',version='1.0.0')

app.add_exception_handler(AppException,app_exception_handler,)
app.add_exception_handler(Exception,generic_exception_handler,)

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(health_router)
app.include_router(website_router)
app.include_router(audio_router)
app.include_router(tts_router)
app.include_router(youtube_router)
app.include_router(agent_router)