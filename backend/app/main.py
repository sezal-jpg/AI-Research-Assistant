from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.website import router as website_router
from app.core.exceptions import(AppException,app_exception_handler,generic_exception_handler,)

app=FastAPI(title='OmniResearch AI',version='1.0.0')

app.add_exception_handler(AppException,app_exception_handler,)
app.add_exception_handler(Exception,generic_exception_handler,)

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(health_router)
app.include_router(website_router)