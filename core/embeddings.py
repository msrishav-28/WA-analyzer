import os
import numpy as np
from typing import List, Tuple, Dict

class EmbeddingEngine:
    """
    V6 SOTA Embedding Engine using BAAI/bge-m3 (Dense, Multilingual, Multimodal-capable)
    or Perplexity API.
    """
    LOCAL_MODEL = 'BAAI/bge-m3'
    API_MODEL   = 'pplx-embed-v1'

    def __init__(self, mode: str = 'local', api_key: str = None):
        self.mode = mode
        self.dim = 1024
        self._model = None
        self._client = None
        
        if mode == 'local':
            self._init_local()
        elif mode == 'api':
            self._init_api(api_key)
        else:
            raise ValueError("Only 'local' and 'api' modes supported in V6.")

    def _init_local(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.LOCAL_MODEL)
            print(f"✅  Loaded V6 Local Model: {self.LOCAL_MODEL} (1024-dim, Multilingual)")
        except ImportError:
            raise ImportError("Please install sentence-transformers.")

    def _init_api(self, api_key: str):
        key = api_key or os.environ.get('PPLX_API_KEY')
        if not key:
            raise ValueError("PPLX_API_KEY not set!")
        from openai import OpenAI
        self._client = OpenAI(api_key=key, base_url="https://api.perplexity.ai")
        print(f"✅  Loaded V6 API Model: {self.API_MODEL}")

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.mode == 'api':
            return self._encode_api(texts)
        return self._encode_local(texts)

    def _encode_local(self, texts: List[str]) -> np.ndarray:
        return self._model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)

    def _encode_api(self, texts: List[str]) -> np.ndarray:
        from sklearn.preprocessing import normalize
        all_embs = []
        for i in range(0, len(texts), 100):
            resp = self._client.embeddings.create(model=self.API_MODEL, input=texts[i:i+100])
            all_embs.extend(e.embedding for e in resp.data)
        return normalize(np.array(all_embs, dtype=np.float32))
