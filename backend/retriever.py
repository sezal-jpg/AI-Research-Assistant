from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_docs(question, docs):

    pairs = [(question, doc.page_content) for doc in docs]

    scores = reranker.predict(pairs)

    ranked_docs = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    return ranked_docs
