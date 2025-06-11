from typing import Dict, List
from sentence_transformers import SentenceTransformer

from embeddings.base_embeddings import BaseEmbeddings


class Embeddings(BaseEmbeddings):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def create_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_numpy=False).tolist()
        return embedding

    def create_embeddings(self, texts: List[str]) -> Dict[str, List[float]]:
        return {t: self.create_embedding(t) for t in texts}


if __name__ == "__main__":
    embeddings = Embeddings()
    object = embeddings.create_embedding("Embed this")
    objects = embeddings.create_embeddings(["Embed this"])
