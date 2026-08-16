import os
import numpy as np
from huggingface_hub import InferenceClient

# Free — this is a personal access token, not a paid subscription.
# Create one at huggingface.co -> profile picture -> Settings ->
# Access Tokens -> New token -> role "Read" is enough.
HF_TOKEN = os.getenv("HF_TOKEN")
EMBED_MODEL = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN)
    return _client


class RemoteEmbeddingModel:
    """Same .encode() interface as your real SentenceTransformer, but
    calls Hugging Face's free hosted Inference API over HTTP instead of
    loading the model anywhere ourselves. Handles both call shapes your
    code uses: a single string (semantic.py) and a list of strings
    (vectorizer.py's batch embed_chunks)."""

    def encode(self, text, **kwargs):
        client = _get_client()
        is_single = isinstance(text, str)
        texts = [text] if is_single else list(text)

        vectors = []
        for t in texts:
            result = client.feature_extraction(t, model=EMBED_MODEL)
            arr = np.array(result)
            # Some models return one vector per token (2D) instead of one
            # pooled sentence vector (1D) — mean-pool if so, so this
            # always returns a single fixed-size vector per text, same
            # shape your pgvector column already expects.
            if arr.ndim == 2:
                arr = arr.mean(axis=0)
            vectors.append(arr)

        arr = np.array(vectors)
        return arr[0] if is_single else arr


_model = None


def get_remote_model():
    global _model
    if _model is None:
        _model = RemoteEmbeddingModel()
    return _model