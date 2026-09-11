import os
from dotenv import load_dotenv
from app.core.config import client,model

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_model():
    return model