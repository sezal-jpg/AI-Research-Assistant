import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client=genai.Client(api_key=GEMINI_API_KEY)

model = "models/gemini-2.5-flash"
ENABLE_GRAPH_CONSTRUCTION = os.getenv(
    "ENABLE_GRAPH_CONSTRUCTION",
    "false"
).lower() == "true"
