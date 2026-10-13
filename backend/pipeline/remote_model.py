import os
import numpy as np
from fastembed import TextEmbedding
 
# Same model as before, so existing Supabase vectors stay compatible.
EMBED_MODEL = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
 
_embedder = None
 
 
def _get_embedder():
    global _embedder
    if _embedder is None:
        # Downloads the small ONNX model on first use, then runs locally.
        _embedder = TextEmbedding(model_name=EMBED_MODEL)
    return _embedder
 
 
class RemoteEmbeddingModel:
    """Kept under the old name so vectorizer.py and the rest of the code
    keep working unchanged. It no longer calls any remote API."""
 
    def encode(self, text, **kwargs):
        is_single = isinstance(text, str)
        texts = [text] if is_single else list(text)
        vectors = np.array(list(_get_embedder().embed(texts)))
        return vectors[0] if is_single else vectors
 
 
_model = None
 
 
def get_remote_model():
    global _model
    if _model is None:
        _model = RemoteEmbeddingModel()
    return _model
 