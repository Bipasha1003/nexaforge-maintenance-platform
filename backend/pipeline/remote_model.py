import os
import requests
import numpy as np

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://127.0.0.1:7860")


class RemoteEmbeddingModel:
    """Mimics the .encode(text) interface of a local SentenceTransformer,
    but calls the Hugging Face Space over HTTP instead of loading the
    model in this process. semantic.py calls `model.encode(query).tolist()`,
    so .encode() has to return something with .tolist() — a numpy array,
    same as the real SentenceTransformer would."""

    def encode(self, text):
        res = requests.post(
            f"{MODEL_SERVICE_URL}/embed",
            json={"text": text},
            timeout=30,
        )
        res.raise_for_status()
        return np.array(res.json()["embedding"])


_model = None


def get_remote_model():
    global _model
    if _model is None:
        _model = RemoteEmbeddingModel()
    return _model