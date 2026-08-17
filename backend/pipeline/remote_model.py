import os
import time
import numpy as np
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")
EMBED_MODEL = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN)
    return _client

class RemoteEmbeddingModel:
    def encode(self, text, **kwargs):
        client = _get_client()
        is_single = isinstance(text, str)
        texts = [text] if is_single else list(text)

        vectors = []
        for t in texts:
            for attempt in range(3):
                try:
                    result = client.feature_extraction(t, model=EMBED_MODEL)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise e
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