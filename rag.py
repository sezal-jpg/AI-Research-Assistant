from config import model
def generate_answer(
    question,
    context
):

    prompt = f"""
You are an AI Research Assistant.

The following context has already been retrieved using:

- Hybrid Search (BM25 + Semantic Search)
- CrossEncoder Reranking

Your task:

1. Understand the user's intent.

2. Internally identify important keywords and concepts.

3. Ignore duplicated information.

4. Ignore irrelevant information.

5. Combine facts from multiple chunks.

6. Answer ONLY using the provided context.

7. If the answer is not present, reply exactly:

"I could not find this information in the uploaded PDFs."

8. Mention the PDF names naturally whenever possible.

Context:

{context}

Question:

{question}

Answer:
"""

    response = model.generate_content(
        prompt
    )

    return response.text
