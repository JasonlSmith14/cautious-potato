from sentence_transformers import SentenceTransformer


class Embeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def create_embedding(self, text: str) -> list[float]:
        embedding = self.model.encode(text, convert_to_numpy=False).tolist()
        return embedding


if __name__ == "__main__":
    embeddings = Embeddings()
    object = embeddings.create_embedding("Embed this")
