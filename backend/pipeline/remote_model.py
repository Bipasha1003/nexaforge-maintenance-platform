import os
import time
import numpy as np
from huggingface_hub import InferenceClient

# Free -- this is a personal access token, not a paid subscription.
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
            # Add a 3-attempt retry loop for cold starts
            for attempt in range(3):
                try:
                    result = client.feature_extraction(t, model=EMBED_MODEL)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e # If it fails 3 times, crash normally
                    print("Hugging Face model waking up... retrying in 5 seconds.")
                    time.sleep(5)
            
            arr = np.array(result)
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