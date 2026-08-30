from app.core.config import model
from app.core.gemini_utils import log_gemini_error

class GenerationService:

 def generate(self,question:str, context:str, history:str):

    prompt = f"""
You are an AI Research Assistant.

You must follow these rules strictly.

RULES

1. Use ONLY the retrieved context.

2. Never use your own knowledge.

3. Never guess.

4. Never fabricate information.

5. Never invent citations.

6.Use the conversation history only to understand follow-up questions.

7. If the context is insufficient,
reply exactly:

"I couldn't find this information in the uploaded PDF(s)."

8. If multiple PDFs contain different information,
mention that.

9. Keep answers concise and factual.


conversation_history:
{history}

 Retrieved Context:

{context}

Question:

{question}

Answer:
"""
    try:
     response = model.generate_content(prompt)
     return response.text
    
    except Exception as e:
        error_type=log_gemini_error('answer generation',e)
        
        if error_type=='quota':
         return ("The AI service is temporarily unavailable "
            "because the Gemini API quota has been reached.")
        return (
        "I couldn't generate an answer at this time."
    )
generation_service=GenerationService()

