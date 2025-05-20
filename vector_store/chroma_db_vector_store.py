from typing import Any, Dict, List
from chromadb import Client, Collection, PersistentClient
from chromadb.config import Settings

class ChromaDBVectorStore:
    def __init__(self, persistence: bool = False, path: str = None):
        if persistence:
            settings = Settings()
            settings.persist_directory  = path
            self.chroma_client = PersistentClient(path=path, settings=settings)
        else:
            self.chroma_client = Client()

    def create_collection(self, name: str):
        return self.chroma_client.get_or_create_collection(name=name)

    def add_to_collection(
        self,
        collection: Collection,
        documents: List[str],
        ids: List[str],
        metadatas: List[Dict[str, Any]] = None,
        embeddings: List[List[int]] = None,
    ):

        collection.upsert(
            documents=documents, ids=ids, metadatas=metadatas, embeddings=embeddings
        )

    def query_collection(
        self,
        collection: Collection,
        query_texts: List[str],
        n_results: int,
        where: Dict[str, Any] = None,
    ):
        return collection.query(
            query_texts=query_texts, n_results=n_results, where=where
        )


if __name__ == "__main__":
    chroma_db_vector_store = ChromaDBVectorStore(persistence=True, path="db/chroma")

    students = chroma_db_vector_store.create_collection(name="Students")

    chroma_db_vector_store.add_to_collection(
        collection=students,
        documents=["Jason bought groceries", "Sarah paid rent"],
        ids=["1", "2"],
        metadatas=[{"category": "food"}, {"category": "rent"}],
    )

    result = chroma_db_vector_store.query_collection(
        collection=students, query_texts=[""], n_results=2, where={"category": "rent"}
    )
