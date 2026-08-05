from app.core.config import model
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
    response = model.generate_content(prompt)

    return response.text
generation_service=GenerationService()

