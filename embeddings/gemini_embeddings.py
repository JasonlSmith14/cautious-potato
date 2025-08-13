from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings

from embeddings.base_embeddings import BaseEmbeddings


class LangchainEmbeddings(BaseEmbeddings):
    def __init__(self, embedding_model: Embeddings):
        self.embedding_model = embedding_model

    def create_embedding(self, text):
        return self.embedding_model.embed_query(text)


if __name__ == "__main__":
    gemini_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    langchain_embeddings = LangchainEmbeddings(embedding_model=gemini_embeddings)

    langchain_embeddings.create_embedding("Embed this text")
