import os
from openai import OpenAI
from typing import List

class OpenAIEmbeddingsClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        self.client = OpenAI(api_key=self.api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        res = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in res.data]
