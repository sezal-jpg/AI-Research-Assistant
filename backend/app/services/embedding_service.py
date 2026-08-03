from langchain_community.embeddings import HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="intfloat/e5-base-v2"
)
def get_embedding_model():
    return embedding_model